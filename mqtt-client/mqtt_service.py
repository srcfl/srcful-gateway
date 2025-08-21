#!/usr/bin/env python3
"""
Simple MQTT Service with Flask API

Basic MQTT service that:
1. Gets its own device credentials from the web container
2. Connects to MQTT broker
3. Provides HTTP API for publishing data
"""

import os
import ssl
import json
import logging
import signal
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from collections import deque
import uuid

from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import requests

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set specific log levels for external libraries to reduce noise
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.INFO)

# Global MQTT client and Flask app
mqtt_client = None
app = Flask(__name__)


class SimpleMQTTClient:
    def __init__(self):
        self.client = None
        self.device_id = None
        self.wallet = None
        self.connected = False
        self.broker_host = os.getenv('MQTT_BROKER_HOST', 'mqtt.srcful.dev')
        self.broker_port = int(os.getenv('MQTT_BROKER_PORT', '8883'))
        self._publish_count = 0
        self._publish_errors = 0
        
        # JWT token management
        self._jwt_token = None
        self._jwt_expires_at = None
        self._serial_number = None
        
        # Cache for wallet address
        self._cached_wallet = None
        
        # Topic-specific publish tracking for last 60 seconds
        self._topic_publishes = {}  # topic -> deque of timestamps
        
    def _clean_old_topic_records(self):
        """Remove publish records older than 10 minutes for all topics."""
        cutoff_time = time.time() - 600  # 10 minutes
        for topic in list(self._topic_publishes.keys()):
            topic_queue = self._topic_publishes[topic]
            # Remove old timestamps
            while topic_queue and topic_queue[0] < cutoff_time:
                topic_queue.popleft()
            # Remove empty queues to keep memory clean
            if not topic_queue:
                del self._topic_publishes[topic]

    def _record_topic_publish(self, topic: str):
        """Record a successful publish to a topic."""
        current_time = time.time()
        if topic not in self._topic_publishes:
            self._topic_publishes[topic] = deque()
        self._topic_publishes[topic].append(current_time)
        # Clean old records periodically
        self._clean_old_topic_records()

    def _get_topic_publish_counts(self) -> Dict[str, Dict[str, int]]:
        """Get publish counts for each topic in different time windows."""
        self._clean_old_topic_records()
        current_time = time.time()
        
        result = {}
        for topic, timestamps in self._topic_publishes.items():
            # Count messages in different time windows
            count_60s = sum(1 for ts in timestamps if current_time - ts <= 60)
            count_5m = sum(1 for ts in timestamps if current_time - ts <= 300)  # 5 minutes
            count_10m = sum(1 for ts in timestamps if current_time - ts <= 600)  # 10 minutes
            
            result[topic] = {
                '60s': count_60s,
                '5m': count_5m,
                '10m': count_10m
            }
        
        return result

    def on_connect(self, client, userdata, flags, rc):
        """Called when the broker responds to our connection request."""
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.connected = True
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")
            self.connected = False

    def on_disconnect(self, client, userdata, rc):
        """Called when the client disconnects from the broker."""
        logger.warning(f"Disconnected from MQTT broker with result code {rc}")
        self.connected = False

    def on_publish(self, client, userdata, mid):
        """Called when a message that was to be sent using the publish() call has completed transmission to the broker."""
        logger.debug(f"Message {mid} published successfully")
        self._publish_count += 1

    def on_log(self, client, userdata, level, buf):
        """Called when the client has log information."""
        log_levels = {
            mqtt.MQTT_LOG_DEBUG: logger.debug,
            mqtt.MQTT_LOG_INFO: logger.info,
            mqtt.MQTT_LOG_NOTICE: logger.info,
            mqtt.MQTT_LOG_WARNING: logger.warning,
            mqtt.MQTT_LOG_ERR: logger.error
        }
        log_func = log_levels.get(level, logger.info)
        log_func(f"MQTT: {buf}")

    def get_crypto_info(self) -> Dict[str, Any]:
        """Get crypto information from web container"""
        try:
            web_host = os.getenv('WEB_CONTAINER_HOST', 'localhost')
            web_port = os.getenv('WEB_CONTAINER_PORT', '5000')
            url = f"http://{web_host}:{web_port}/api/crypto"
            
            logger.debug(f"Requesting crypto info from: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            crypto_info = response.json()
            logger.info(f"Serial number: {crypto_info.get('serialNumber', 'NOT_FOUND')}")
            
            return crypto_info
            
        except Exception as e:
            logger.error(f"Failed to get crypto info: {e}")
            raise

    def get_owner_wallet(self) -> str:
        """Get owner wallet address from web container (cached)"""
        # Return cached wallet if available
        if self._cached_wallet:
            logger.debug(f"Using cached wallet address: {self._cached_wallet}")
            return self._cached_wallet
            
        try:
            web_host = os.getenv('WEB_CONTAINER_HOST', 'localhost')
            web_port = os.getenv('WEB_CONTAINER_PORT', '5000')
            url = f"http://{web_host}:{web_port}/api/owner"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            owner_info = response.json()
            wallet = owner_info.get('wallet')
            
            if not wallet:
                raise ValueError("No wallet found in owner info")
            
            # Cache the wallet address
            self._cached_wallet = wallet
            logger.info(f"Got and cached wallet address: {wallet}")
            return wallet
            
        except Exception as e:
            logger.error(f"Failed to get owner wallet: {e}")
            raise

    def create_jwt_token(self, serial_number: str) -> str:
        """Create JWT token for MQTT authentication"""
        try:
            web_host = os.getenv('WEB_CONTAINER_HOST', 'localhost')
            web_port = os.getenv('WEB_CONTAINER_PORT', '5000')
            
            # Prepare JWT payload
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(hours=23)  # Refresh 1 hour before expiry
            
            payload = {
                'iat': now.isoformat(),
                'exp': (now + timedelta(hours=24)).isoformat(),  # 24 hour expiry
                'jti': str(uuid.uuid4())
            }
            
            headers = {
                'alg': 'ES256',
                'typ': 'JWT',
                'opr': 'production',
                'device': serial_number
            }
            
            jwt_request = {
                'headers': headers,
                'barn': payload,
                'expires_in': 1440  # 24 hours in minutes
            }
            
            url = f"http://{web_host}:{web_port}/api/jwt/create"
            
            response = requests.post(url, json=jwt_request, timeout=10)
            response.raise_for_status()
            
            jwt_response = response.json()
            jwt_token = jwt_response.get('jwt')
            
            if not jwt_token:
                raise ValueError("No JWT token in response")
            
            # Store token and expiry for refresh logic
            self._jwt_token = jwt_token
            self._jwt_expires_at = expires_at
            self._serial_number = serial_number
            
            logger.info(f"JWT token created successfully, expires at: {expires_at.isoformat()}")
            return jwt_token
            
        except Exception as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise

    def setup_tls(self):
        """Configure TLS settings"""
        try:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            
            # Try custom CA certificate
            ca_cert_content = os.getenv('MQTT_ROOT_CA')
            if ca_cert_content:
                ca_cert_path = '/tmp/ca-cert.pem'
                with open(ca_cert_path, 'w') as f:
                    f.write(ca_cert_content)
                context.load_verify_locations(ca_cert_path)
            
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            self.client.tls_set_context(context)
            
        except Exception as e:
            logger.error(f"Failed to setup TLS: {e}")
            raise

    def connect(self) -> bool:
        """Connect to MQTT broker with device credentials."""
        try:
            logger.info(f"Starting MQTT connection to {self.broker_host}:{self.broker_port}")
            
            # Get device credentials
            crypto_info = self.get_crypto_info()
            serial_number = crypto_info.get('serialNumber')
            
            if not serial_number:
                raise ValueError("No serialNumber found in crypto info")
            
            # Get owner wallet address to use as client ID
            wallet_address = self.get_owner_wallet()
            
            # Create JWT token
            jwt_token = self.create_jwt_token(serial_number)
            
            # Initialize MQTT client with wallet address as client ID
            self.device_id = serial_number
            self.wallet = wallet_address
            self.client = mqtt.Client(client_id=serial_number)
            self.client.username_pw_set(wallet_address, jwt_token)
            
            # Set callbacks
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            self.client.on_log = self.on_log

            # Setup TLS
            self.setup_tls()

            # Connect to broker
            logger.info(f"Connecting to MQTT broker {self.broker_host}:{self.broker_port}...")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 30
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                logger.info("Successfully connected to MQTT broker")
                return True
            else:
                logger.error("Connection timeout")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False

    def publish(self, topic: str, payload: Dict[str, Any], qos: int = 0) -> bool:
        """Publish a message to the MQTT broker."""
        if not self.connected or not self.client:
            logger.error("Cannot publish: not connected to MQTT broker")
            self._publish_errors += 1
            return False

        try:
            message_json = json.dumps(payload)
            result = self.client.publish(topic, message_json, qos=qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {topic}: {message_json}")
                self._publish_count += 1
                # Record the topic-specific publish
                self._record_topic_publish(topic)
                return True
            else:
                logger.error(f"Failed to publish to {topic}, error code: {result.rc}")
                self._publish_errors += 1
                return False
                
        except Exception as e:
            logger.error(f"Exception while publishing to {topic}: {e}")
            self._publish_errors += 1
            return False

    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("Disconnected from MQTT broker")

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return {
            'connected': self.connected,
            'device_id': self.device_id,
            'broker': f"{self.broker_host}:{self.broker_port}",
            'publish_count': self._publish_count,
            'publish_errors': self._publish_errors,
            'success_rate': (self._publish_count / (self._publish_count + self._publish_errors)) * 100 if (self._publish_count + self._publish_errors) > 0 else 0,
            'topic_publish_counts': self._get_topic_publish_counts()
        }


# Flask API endpoints
@app.route('/publish', methods=['POST'])
def publish_message():
    """Publish a message via HTTP POST."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Validate required fields
        if 'topic' not in data or 'payload' not in data:
            return jsonify({'error': 'Missing required fields: topic, payload'}), 400

        # Use topic and payload as provided by server
        topic = f"sourceful/{mqtt_client.wallet}/{data['topic']}"
        payload = data['payload']
        qos = data.get('qos', 0)

        if not mqtt_client or not mqtt_client.connected:
            return jsonify({'error': 'MQTT client not connected'}), 503

        success = mqtt_client.publish(topic, payload, qos)
        
        if success:
            return jsonify({'status': 'published', 'topic': topic})
        else:
            return jsonify({'error': 'Failed to publish message'}), 500

    except Exception as e:
        logger.error(f"Error in publish endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def get_status():
    """Get MQTT client status."""
    if mqtt_client:
        return jsonify(mqtt_client.get_stats())
    else:
        return jsonify({'error': 'MQTT client not initialized'}), 503


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now(timezone.utc).isoformat()})


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    if mqtt_client:
        mqtt_client.disconnect()
    sys.exit(0)


def main():
    """Main function to start the MQTT service."""
    global mqtt_client
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Simple MQTT Service")
    
    # Initialize MQTT client
    mqtt_client = SimpleMQTTClient()
    
    # Connect to MQTT broker
    if not mqtt_client.connect():
        logger.error("Failed to connect to MQTT broker, exiting")
        sys.exit(1)
    
    # Start Flask app
    port = int(os.getenv('PORT', 8090))
    logger.info(f"Starting Flask app on port {port}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
