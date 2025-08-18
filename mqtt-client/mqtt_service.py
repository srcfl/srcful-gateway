#!/usr/bin/env python3
"""
Simple MQTT Service with Flask API

Self-initializing MQTT service that:
1. Gets its own device credentials from the web container
2. Connects to MQTT broker automatically
3. Provides HTTP API for publishing data
"""

import os
import ssl
import json
import logging
import signal
import sys
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import uuid

from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global MQTT client and Flask app
mqtt_client = None
app = Flask(__name__)


class SelfInitializingMQTTClient:
    def __init__(self):
        self.client = None
        self.device_id = None
        self.connected = False
        self.broker_host = os.getenv('MQTT_BROKER_HOST', 'mqtt.srcful.dev')
        self.broker_port = int(os.getenv('MQTT_BROKER_PORT', '8883'))
        
    def get_crypto_info(self) -> Dict[str, Any]:
        """Get crypto information from web container"""
        try:
            web_host = os.getenv('WEB_CONTAINER_HOST', 'localhost')
            web_port = os.getenv('WEB_CONTAINER_PORT', '5000')
            url = f"http://{web_host}:{web_port}/api/crypto"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            crypto_info = response.json()
            return crypto_info
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to web container: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout connecting to web container: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get crypto info: {e}")
            raise

    def create_jwt_token(self, serial_number: str) -> str:
        """Create JWT token for MQTT authentication"""
        try:
            web_host = os.getenv('WEB_CONTAINER_HOST', 'localhost')
            web_port = os.getenv('WEB_CONTAINER_PORT', '5000')
            
            # Prepare JWT payload
            now = datetime.now(timezone.utc)
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
                
            return jwt_token
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to web container for JWT: {e}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error creating JWT: {e.response.status_code}")
            raise
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
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for connection"""
        if rc == 0:
            logger.info("MQTT connected successfully")
            self.connected = True
        else:
            logger.error(f"MQTT connection failed with code {rc}")
            # Decode return codes
            rc_meanings = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier", 
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorised"
            }
            meaning = rc_meanings.get(rc, f"Unknown error code {rc}")
            logger.error(f"MQTT Error: {meaning}")
            self.connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for disconnection"""
        logger.warning(f"MQTT disconnected (rc={rc})")
        self.connected = False
    
    def initialize_and_connect(self, max_retries: int = 5, retry_delay: int = 5) -> bool:
        """Initialize MQTT connection with device credentials"""
        for attempt in range(max_retries):
            try:
                # Get device credentials
                crypto_info = self.get_crypto_info()
                serial_number = crypto_info.get('serialNumber')
                
                if not serial_number:
                    raise ValueError("No serialNumber found in crypto info")
                
                # Create JWT token
                jwt_token = self.create_jwt_token(serial_number)
                
                # Initialize MQTT client
                self.device_id = serial_number
                self.client = mqtt.Client(client_id=serial_number)
                self.client.username_pw_set(serial_number, jwt_token)
                self.client.on_connect = self.on_connect
                self.client.on_disconnect = self.on_disconnect
                
                # Setup TLS
                self.setup_tls()
                
                # Connect to broker
                self.client.connect(self.broker_host, self.broker_port, 60)
                self.client.loop_start()
                
                # Wait a moment to see if connection succeeds
                time.sleep(3)  # Increased wait time
                
                if self.connected:
                    logger.info(f"MQTT initialized for device {serial_number}")
                    return True
                else:
                    logger.warning(f"MQTT connection failed, attempt {attempt + 1}/{max_retries}")
                    
            except Exception as e:
                logger.error(f"MQTT initialization error (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        
        logger.error("MQTT initialization failed after all retries")
        return False
    
    def publish(self, topic: str, payload: Dict[str, Any]) -> bool:
        """Publish message to MQTT"""
        if not self.client or not self.connected:
            logger.error("MQTT client not connected")
            return False
            
        try:
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                return True
            else:
                logger.error(f"Failed to publish to {topic}, error code: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing to MQTT: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False


# Flask Routes

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    global mqtt_client
    return jsonify({
        "status": "healthy",
        "mqtt_connected": mqtt_client.connected if mqtt_client else False,
        "device_id": mqtt_client.device_id if mqtt_client else None,
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/publish', methods=['POST'])
def publish():
    """Publish data to MQTT topic"""
    global mqtt_client
    
    try:
        data = request.get_json()
        
        # Log incoming request body for debugging
        logger.info(f"Incoming POST request body: {json.dumps(data, indent=2) if data else 'None'}")
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        if 'topic' not in data or 'payload' not in data:
            return jsonify({"error": "Missing required fields: topic, payload"}), 400
        
        if not mqtt_client or not mqtt_client.connected:
            return jsonify({"error": "MQTT client not connected"}), 503
        
        # Use topic and payload as provided by server
        topic = data['topic']
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            **data['payload']
        }
        
        # Log what we're publishing for debugging
        logger.info(f"Publishing to topic '{topic}': {json.dumps(payload, indent=2)}")
        
        # Publish to MQTT
        success = mqtt_client.publish(topic, payload)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Data published successfully",
                "topic": topic
            })
        else:
            return jsonify({"error": "Failed to publish to MQTT"}), 500
            
    except Exception as e:
        logger.error(f"Error in publish endpoint: {e}")
        return jsonify({"error": str(e)}), 500


def initialize_mqtt_in_background():
    """Initialize MQTT in a separate thread"""
    global mqtt_client
    
    mqtt_client = SelfInitializingMQTTClient()
    
    # Try to initialize with retries
    success = mqtt_client.initialize_and_connect()
    
    if not success:
        logger.error("MQTT initialization failed - service will run without MQTT connection")
        # Don't exit - keep the HTTP API running even if MQTT fails


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    global mqtt_client
    if mqtt_client:
        mqtt_client.disconnect()
    sys.exit(0)


def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configuration
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', '8090'))  # Changed from 8080 to avoid conflict with Traefik
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting MQTT Service on {host}:{port}")
    
    # Start MQTT initialization in background
    mqtt_thread = threading.Thread(target=initialize_mqtt_in_background, daemon=True)
    mqtt_thread.start()
    
    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
