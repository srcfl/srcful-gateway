#!/usr/bin/env python3
"""
MQTT Service for Srcful Gateway

Standalone MQTT service that:
1. Connects to MQTT broker with device credentials
2. Provides publish/subscribe functionality 
3. Can be used by multiple components via blackboard
"""

import os
import ssl
import json
import logging
import time
from typing import Dict, Any, List, Callable, Optional
from collections import deque
import threading
from server.devices.supported_devices.data_models import DERData
import paho.mqtt.client as mqtt
import server.crypto.crypto as crypto

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class MQTTService:
    def __init__(self, device_serial: str, wallet_address: str, jwt_token: str):
        self.device_serial = device_serial
        self.wallet_address = wallet_address
        self.jwt_token = jwt_token
        self.client = None
        self.connected = False
        self.broker_host = os.getenv('MQTT_BROKER_HOST', 'mqtt.srcful.dev')
        self.broker_port = int(os.getenv('MQTT_BROKER_PORT', '8883'))
        self._publish_count = 0
        self._publish_errors = 0
        self._running = False
        self._thread = None
        self._client_id = None
        
        # Topic-specific publish tracking
        self._topic_publishes = {}  # topic -> deque of timestamps
        
        # Message callbacks for different topics
        self._message_callbacks: Dict[str, List[Callable]] = {}

    @classmethod
    def create_and_start(cls, blackboard, wallet_address: str) -> 'MQTTService':
        """Create and start MQTT service with wallet address."""
        from datetime import datetime, timezone, timedelta
        import uuid
        
        try:
            # Get device credentials from crypto state
            device_serial = blackboard.crypto_state().serial_number.hex()
            
            # Create JWT token
            now = datetime.now(timezone.utc)
            payload = {
                'iat': now.isoformat(),
                'exp': (now + timedelta(hours=24)).isoformat(),
                'jti': str(uuid.uuid4())
            }
            
            headers = {
                'alg': 'ES256',
                'typ': 'JWT',
                'opr': 'production',
                'device': device_serial
            }
            
            with crypto.Chip() as chip:
                jwt = chip.build_jwt(data_2_sign=payload, headers=headers, retries=5)
                # Create and start MQTT service
                mqtt_service = cls(device_serial, wallet_address, jwt)
                mqtt_service.start()
                logger.info(f"MQTT service created and started for wallet: {wallet_address}")
                return mqtt_service
            
        except Exception as e:
            logger.error(f"Failed to create MQTT service: {e}")
            raise
        
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

    def add_message_callback(self, topic_pattern: str, callback: Callable[[str, Dict[str, Any]], None]):
        """Add a callback function for messages on specific topics."""
        if topic_pattern not in self._message_callbacks:
            self._message_callbacks[topic_pattern] = []
        self._message_callbacks[topic_pattern].append(callback)

    def remove_message_callback(self, topic_pattern: str, callback: Callable):
        """Remove a callback function."""
        if topic_pattern in self._message_callbacks:
            self._message_callbacks[topic_pattern] = [
                cb for cb in self._message_callbacks[topic_pattern] if cb != callback
            ]

    def on_connect(self, client, userdata, flags, rc):
        """Called when the broker responds to our connection request."""
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.connected = True

            # Store client ID for topic building
            self._client_id = client._client_id.decode('utf-8') if isinstance(client._client_id, bytes) else client._client_id

            # Note: Topic subscriptions are now handled by specific services (e.g., control_task_subscription)
            # rather than automatically subscribing here
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")
            self.connected = False

    def on_disconnect(self, client, userdata, rc):
        """Called when the client disconnects from the broker."""
        logger.warning(f"Disconnected from MQTT broker with result code {rc}")
        self.connected = False
        
        # For connection lost errors (rc=7), force client cleanup to avoid stale state
        if rc == 7:
            logger.info("Connection lost detected, will recreate client on next connection attempt")
            self._cleanup_client()

    def on_publish(self, client, userdata, mid):
        """Called when a message that was to be sent using the publish() call has completed transmission to the broker."""
        logger.debug(f"Message {mid} published successfully")
        self._publish_count += 1

    def on_message(self, client, userdata, msg):
        """Called when a message has been received on a topic that the client subscribes to."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            logger.info(f"Received message on topic '{topic}'")
            
            # Try to parse as JSON
            try:
                json_data = json.loads(payload)
                logger.info(f"JSON payload: {json.dumps(json_data, indent=2)}")
                
                # Call registered callbacks
                for topic_pattern, callbacks in self._message_callbacks.items():
                    if topic_pattern in topic or topic_pattern == "*":
                        for callback in callbacks:
                            try:
                                callback(topic, json_data)
                            except Exception as e:
                                logger.error(f"Error in message callback: {e}")
                                
            except json.JSONDecodeError:
                logger.info(f"Raw payload: {payload}")
                
        except Exception as e:
            logger.error(f"Error processing received message: {e}")

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

    def _cleanup_client(self):
        """Clean up the current MQTT client to avoid stale state."""
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception as e:
                logger.debug(f"Error during client cleanup: {e}")
            finally:
                self.client = None
                self.connected = False

    def setup_tls(self):
        """Configure TLS settings"""
        if not self.client:
            raise Exception("Cannot setup TLS: MQTT client not initialized")
            
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
            
            # Clean up any existing client to avoid stale state
            if self.client:
                self._cleanup_client()
            
            # Initialize MQTT client
            self.client = mqtt.Client(client_id=self.device_serial)
            self.client.username_pw_set(self.wallet_address, self.jwt_token)
            
            # Set callbacks
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            self.client.on_message = self.on_message
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
                self._cleanup_client()  # Clean up on timeout
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            self._cleanup_client()  # Clean up on error
            return False

    def build_topic(self, prefix: str, subtopic: str = "") -> str:
        """Build a topic with the format: prefix/client_id/subtopic"""
        if not self._client_id:
            raise Exception("Cannot build topic: client ID not available (not connected)")
        
        topic = f"{prefix}/{self._client_id}"
        if subtopic:
            topic = f"{topic}/{subtopic}"
        return topic

    def publish_telemetry(self, topic: str, payload: Dict[str, Any], qos: int = 0) -> bool:
        """Convenience method to publish telemetry data."""
        return self.publish(topic, payload, qos, prefix="telemetry")
    
    def publish_control(self, topic: str, payload: Dict[str, Any], qos: int = 0) -> bool:
        """Convenience method to publish control data."""
        return self.publish(topic, payload, qos, prefix="control")
    
    def publish_status(self, topic: str, payload: Dict[str, Any], qos: int = 0) -> bool:
        """Convenience method to publish status data."""
        return self.publish(topic, payload, qos, prefix="status")

    def publish(self, topic: str, payload: Dict[str, Any], qos: int = 0, prefix: str = "telemetry") -> bool:
        """Publish a message to the MQTT broker."""
        if not self.connected or not self.client:
            logger.error("Cannot publish: not connected to MQTT broker")
            self._publish_errors += 1
            return False

        full_topic = self.build_topic(prefix, topic)
        
        # logger.info(f"Publishing to topic '{full_topic}' with payload: {json.dumps(payload)}")

        try:
            message_json = json.dumps(payload)
            result = self.client.publish(full_topic, message_json, qos=qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {full_topic}: {message_json}")
                self._publish_count += 1
                # Record the topic-specific publish
                self._record_topic_publish(full_topic)
                return True
            else:
                logger.error(f"Failed to publish to {full_topic}, error code: {result.rc}")
                # Error code 4 = MQTT_ERR_NO_CONN (not connected)
                if result.rc == 4:
                    logger.info("Detected connection lost, triggering reconnect")
                    self.connected = False
                self._publish_errors += 1
                return False
                
        except Exception as e:
            logger.error(f"Exception while publishing to {full_topic}: {e}")
            self._publish_errors += 1
            return False
        

    def subscribe(self, topic: str, qos: int = 0, prefix: Optional[str] = None) -> bool:
        """Subscribe to a topic. If prefix is provided, builds topic as prefix/client_id/topic."""
        if not self.connected or not self.client:
            logger.error("Cannot subscribe: not connected to MQTT broker")
            return False

        if prefix:
            full_topic = self.build_topic(prefix, topic)
        else:
            full_topic = topic

        try:
            result, mid = self.client.subscribe(full_topic, qos=qos)
            
            if result == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Successfully subscribed to topic: {full_topic}")
                return True
            else:
                logger.error(f"Failed to subscribe to {full_topic}, error code: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Exception while subscribing to {full_topic}: {e}")
            return False

    def subscribe_control(self, topic: str = "#", qos: int = 0) -> bool:
        """Convenience method to subscribe to control topics."""
        return self.subscribe(topic, qos, prefix="control")

    def start(self):
        """Start the MQTT service in a separate thread."""
        if self._running:
            logger.warning("MQTT service already running")
            return
            
        logger.info("Starting MQTT service")
        self._running = True
        
        # Connect in a separate thread to avoid blocking
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        """Main run loop for MQTT service."""
        retry_delay = 5
        max_retry_delay = 60
        
        while self._running:
            try:
                if not self.connected:
                    logger.info("Attempting to connect to MQTT broker...")
                    if self.connect():
                        retry_delay = 5  # Reset retry delay on success
                    else:
                        logger.error(f"Failed to connect, retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        # Exponential backoff with jitter to avoid thundering herd
                        retry_delay = min(retry_delay * 1.5, max_retry_delay)
                else:
                    time.sleep(1)  # Just sleep if connected
                    
            except Exception as e:
                logger.error(f"Error in MQTT service main loop: {e}")
                # Clean up on unexpected errors
                self._cleanup_client()
                time.sleep(retry_delay)

    def stop(self):
        """Stop the MQTT service."""
        logger.info("Stopping MQTT service")
        self._running = False
        
        # Clean up the client connection
        self._cleanup_client()
            
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return {
            'connected': self.connected,
            'device_serial': self.device_serial,
            'wallet_address': self.wallet_address,
            'broker': f"{self.broker_host}:{self.broker_port}",
            'publish_count': self._publish_count,
            'publish_errors': self._publish_errors,
            'success_rate': (self._publish_count / (self._publish_count + self._publish_errors)) * 100 if (self._publish_count + self._publish_errors) > 0 else 0,
            'topic_publish_counts': self._get_topic_publish_counts()
        }
