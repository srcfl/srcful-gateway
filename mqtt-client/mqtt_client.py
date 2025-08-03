#!/usr/bin/env python3
"""
MQTT Client for Srcful Gateway
- Subscribes to iamcat/control topic for modbus commands
- Publishes modbus responses to iamcat/data topic  
- Publishes gateway state to iamcat/state topic every 5 seconds
- Uses TLS connection with certificate authentication
- Bridges MQTT commands to HTTP requests to web container
"""

import os
import ssl
import json
import time
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, Any
import paho.mqtt.client as mqtt
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SrcfulMQTTClient:
    def __init__(self):
        """Initialize MQTT client with TLS configuration"""
        # Load environment variables from mqtt.env file
        load_dotenv('mqtt.env')

        self.client = mqtt.Client()
        self.setup_tls()
        self.setup_callbacks()
        self.running = True

        # MQTT connection parameters from environment
        self.broker_host = os.getenv('MQTT_BROKER_HOST', 'localhost')
        self.broker_port = int(os.getenv('MQTT_BROKER_PORT', '8883'))
        self.username = os.getenv('MQTT_USERNAME')
        self.password = os.getenv('MQTT_PASSWORD')

        # Web container configuration
        self.web_host = os.getenv('WEB_CONTAINER_HOST', 'web')
        self.web_port = os.getenv('WEB_CONTAINER_PORT', '5000')
        self.web_base_url = f"http://{self.web_host}:{self.web_port}"

        # Topics
        self.control_topic = 'iamcat/control'
        self.modbus_request_topic = 'iamcat/modbus/request'
        self.modbus_response_topic = 'iamcat/modbus/response'
        self.state_topic = 'iamcat/state'

        logger.info(f"Initialized MQTT client for broker {self.broker_host}:{self.broker_port}")

    def setup_tls(self):
        """Configure TLS settings with root CA certificate"""
        try:
            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

            # Try custom CA certificate first
            ca_cert_content = os.getenv('MQTT_ROOT_CA')
            if ca_cert_content:
                try:
                    ca_cert_path = '/tmp/ca-cert.pem'
                    with open(ca_cert_path, 'w') as f:
                        f.write(ca_cert_content)
                    context.load_verify_locations(ca_cert_path)
                    logger.info("Using custom CA certificate")
                except Exception as e:
                    logger.warning(f"Failed to load custom CA certificate: {e}, falling back to system CA store")

            # For EMQX Cloud, enable hostname verification
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED

            # Set TLS version (require TLS 1.2 or higher)
            context.minimum_version = ssl.TLSVersion.TLSv1_2

            self.client.tls_set_context(context)
            logger.info("TLS configuration completed")

        except Exception as e:
            logger.error(f"Failed to setup TLS: {e}")
            raise

    def setup_callbacks(self):
        """Setup MQTT client callbacks"""
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_log = self.on_log

    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client receives a CONNACK response from the server"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            # Subscribe to control and modbus request topics
            client.subscribe(self.control_topic)
            logger.info(f"Subscribed to {self.control_topic}")
            client.subscribe(self.modbus_request_topic)
            logger.info(f"Subscribed to {self.modbus_request_topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker"""
        if rc != 0:
            logger.warning("Unexpected disconnection from MQTT broker")
        else:
            logger.info("Disconnected from MQTT broker")

    def on_message(self, client, userdata, msg):
        """Callback for when a PUBLISH message is received from the server"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            logger.info(f"Received message on {topic}: {payload}")

            if topic == self.control_topic:
                self.handle_control_message(payload)
            elif topic == self.modbus_request_topic:
                self.handle_modbus_request(payload)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def on_log(self, client, userdata, level, buf):
        """Callback for MQTT client logging"""
        logger.debug(f"MQTT Log: {buf}")

    def handle_control_message(self, payload: str):
        """Handle general control messages (non-modbus commands)"""
        try:
            control_data = json.loads(payload)
            logger.info(f"Processing control command: {control_data}")

            # Handle general control commands
            command = control_data.get('command')
            if command == 'start_harvest':
                self.start_harvest_simulation()
            elif command == 'stop_harvest':
                self.stop_harvest_simulation()
            elif command == 'get_status':
                self.publish_status()
            else:
                logger.warning(f"Unknown command: {command}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in control message: {e}")
        except Exception as e:
            logger.error(f"Error handling control message: {e}")

    def handle_modbus_request(self, payload: str):
        """Handle modbus request messages"""
        try:
            modbus_data = json.loads(payload)
            logger.info(f"Processing modbus request: {modbus_data}")

            # Check for function_code to validate it's a modbus command
            function_code = modbus_data.get('function_code')
            if function_code:
                self.handle_modbus_operation(modbus_data)
            else:
                logger.warning(f"Modbus request missing function_code: {modbus_data}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in modbus request: {e}")
        except Exception as e:
            logger.error(f"Error handling modbus request: {e}")

    def handle_modbus_operation(self, control_data: Dict[str, Any]):
        """Handle modbus read/write operations"""
        try:
            function_code = control_data.get('function_code')
            device_id = control_data.get('device_id')
            address = control_data.get('address')

            if not all([function_code, device_id, address]):
                logger.error("Missing required modbus parameters: function_code, device_id, address")
                return

            if function_code in [3, 4]:
                # Read operations (function codes 3 and 4)
                response = self.modbus_read(control_data)
            elif function_code == 16:
                # Write operation (function code 16)
                response = self.modbus_write(control_data)
            else:
                logger.warning(f"Unsupported function code: {function_code}")
                return

            # Publish the response to data topic
            if response:
                self.publish_modbus_response(response, control_data)

        except Exception as e:
            logger.error(f"Error handling modbus operation: {e}")

    def modbus_read(self, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform modbus read operation"""
        try:
            # Extract parameters for read operation
            device_id = control_data.get('device_id')
            function_code = control_data.get('function_code')
            address = control_data.get('address')
            size = control_data.get('size', 1)
            data_type = control_data.get('type', 'U16')
            endianess = control_data.get('endianess', 'big')
            scale_factor = control_data.get('scale_factor', 1)

            # Build URL for read operation
            url = f"{self.web_base_url}/api/inverter/modbus"
            params = {
                'device_id': device_id,
                'function_code': function_code,
                'address': address,
                'size': size,
                'type': data_type,
                'endianess': endianess,
                'scale_factor': scale_factor
            }

            logger.info(f"Making modbus read request: {url} with params: {params}")

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Modbus read response: {result}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed for modbus read: {e}")
            return None
        except Exception as e:
            logger.error(f"Error performing modbus read: {e}")
            return None

    def modbus_write(self, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform modbus write operation"""
        try:
            # Extract parameters for write operation
            device_id = control_data.get('device_id')
            address = control_data.get('address')
            function_code = control_data.get('function_code')
            values = control_data.get('values')
            data_type = control_data.get('type', 'U16')

            if values is None:
                logger.error("Missing 'values' parameter for write operation")
                return None

            # Build URL for write operation
            url = f"{self.web_base_url}/api/inverter/modbus"
            params = {
                'device_id': device_id,
                'address': address,
                'function_code': function_code,
                'values': values,
                'type': data_type
            }

            logger.info(f"Making modbus write request: {url} with params: {params}")

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Modbus write response: {result}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed for modbus write: {e}")
            return None
        except Exception as e:
            logger.error(f"Error performing modbus write: {e}")
            return None

    def publish_modbus_response(self, response: Dict[str, Any], original_request: Dict[str, Any]):
        """Publish modbus operation response to modbus response topic"""
        try:
            response_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "modbus_response",
                "request": original_request,
                "response": response
            }

            payload = json.dumps(response_data)
            result = self.client.publish(self.modbus_response_topic, payload, qos=1)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published modbus response: {payload}")
            else:
                logger.error(f"Failed to publish modbus response, error code: {result.rc}")

        except Exception as e:
            logger.error(f"Error publishing modbus response: {e}")

    def start_harvest_simulation(self):
        """Start simulating harvest data publication"""
        logger.info("Starting harvest data simulation")
        # This would be replaced with actual harvest data collection logic

    def stop_harvest_simulation(self):
        """Stop harvest data simulation"""
        logger.info("Stopping harvest data simulation")

    def publish_harvest_data(self, data: Dict[str, Any]):
        """Publish harvest data to /data topic"""
        try:
            payload = json.dumps(data)
            result = self.client.publish(self.data_topic, payload, qos=1)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published harvest data: {payload}")
            else:
                logger.error(f"Failed to publish harvest data, error code: {result.rc}")

        except Exception as e:
            logger.error(f"Error publishing harvest data: {e}")

    def publish_status(self):
        """Publish current status to /data topic"""
        status_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "status",
            "status": "online",
            "uptime": time.time(),
            "version": "1.0.0"
        }
        self.publish_harvest_data(status_data)

    def fetch_gateway_state(self) -> Dict[str, Any]:
        """Fetch gateway state from web container API"""
        try:
            url = f"{self.web_base_url}/api/state"
            logger.debug(f"Fetching gateway state from: {url}")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            state_data = response.json()
            logger.debug(f"Gateway state response: {state_data}")

            # Add timestamp and type for consistency
            state_data.update({
                "timestamp": datetime.utcnow().isoformat(),
                "type": "gateway_state"
            })

            return state_data

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed for gateway state: {e}")
            return self.get_fallback_state()
        except Exception as e:
            logger.error(f"Error fetching gateway state: {e}")
            return self.get_fallback_state()

    def get_fallback_state(self) -> Dict[str, Any]:
        """Return fallback state when API is unavailable"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "gateway_state",
            "status": "api_unavailable",
            "uptime": time.time(),
            "version": "1.0.0",
            "error": "Failed to fetch state from web container"
        }

    def publish_state(self, state_data: Dict[str, Any]):
        """Publish gateway state to state topic"""
        try:
            payload = json.dumps(state_data)
            result = self.client.publish(self.state_topic, payload, qos=1)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published gateway state: {payload}")
            else:
                logger.error(f"Failed to publish gateway state, error code: {result.rc}")

        except Exception as e:
            logger.error(f"Error publishing gateway state: {e}")

    def connect(self):
        """Connect to MQTT broker"""
        try:
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
                logger.info("MQTT credentials configured")

            self.client.connect(self.broker_host, self.broker_port, 60)
            return True

        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False

    def run(self):
        """Main run loop"""
        logger.info("Starting MQTT client...")

        if not self.connect():
            logger.error("Failed to connect to MQTT broker, exiting")
            return

        # Start the loop in a separate thread
        self.client.loop_start()

        # Publish initial status
        time.sleep(2)  # Wait for connection to establish
        self.publish_status()

        # Main loop - publish gateway state periodically
        try:
            while self.running:
                # Fetch and publish gateway state every 5 seconds
                state_data = self.fetch_gateway_state()
                self.publish_state(state_data)

                # Wait for 5 seconds or until interrupted
                for _ in range(5):
                    if not self.running:
                        break
                    time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.shutdown()

    def shutdown(self):
        """Gracefully shutdown the MQTT client"""
        logger.info("Shutting down MQTT client...")
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT client shutdown complete")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        client = SrcfulMQTTClient()
        client.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
