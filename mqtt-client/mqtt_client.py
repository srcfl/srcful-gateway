#!/usr/bin/env python3
"""
MQTT Client for Srcful Gateway

Uses JWT authentication with:
- deviceid: serialNumber (from /api/crypto)
- username: serialNumber (from /api/crypto) 
- password: JWT token (from /api/jwt/create)

- Publishes gateway state to device/{deviceid}/state topic every minute
- Uses TLS connection with JWT authentication
- Fetches state data from /api/state endpoint
"""

import os
import ssl
import json
import time
import logging
import signal
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
import paho.mqtt.client as mqtt
import requests
import uuid

# Configure logging
# DEBUG: Detailed information for debugging (URLs, payloads, detailed responses)
# INFO: Essential flow information (connections, operations, success/failure)
# WARNING/ERROR: Issues and failures
logging.basicConfig(
    level=logging.DEBUG,  # Set to INFO for production
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SrcfulMQTTClient:
    def __init__(self):
        """Initialize MQTT client with TLS configuration"""
        self.client = mqtt.Client()
        self.setup_tls()
        self.setup_callbacks()
        self.running = True

        # MQTT connection parameters from environment
        self.broker_host = os.getenv('MQTT_BROKER_HOST', 'localhost')
        self.broker_port = int(os.getenv('MQTT_BROKER_PORT', '8883'))

        # Web container configuration
        self.web_host = os.getenv('WEB_CONTAINER_HOST', 'web')
        self.web_port = os.getenv('WEB_CONTAINER_PORT', '5000')
        self.web_base_url = f"http://{self.web_host}:{self.web_port}"

        # Device ID will be set during authentication
        self.device_id = None
        
        # State topic (will be set once device_id is known)
        self.state_topic = None

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
            logger.info(f"Device state will be published to: {self.state_topic}")
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
            logger.info(f"Received message on {topic}")
            logger.debug(f"Message payload: {payload}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def on_log(self, client, userdata, level, buf):
        """Callback for MQTT client logging"""
        logger.debug(f"MQTT Log: {buf}")

    def get_crypto_info(self) -> Dict[str, Any]:
        """Get crypto information from web container API"""
        try:
            url = f"{self.web_base_url}/api/crypto"
            logger.debug(f"Fetching crypto info from: {url}")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            crypto_info = response.json()
            logger.info(f"Retrieved serialNumber: {crypto_info.get('serialNumber', 'N/A')}")
            return crypto_info

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get crypto info: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error parsing crypto info: {e}")
            raise e

    def create_jwt_token(self) -> str:
        """Create JWT token using web container API"""
        try:
            # Get crypto info to get serialNumber for JWT subject
            crypto_info = self.get_crypto_info()
            serial_number = crypto_info.get('serialNumber')
            
            if not serial_number:
                raise ValueError("No serialNumber found in crypto info")

            # Prepare JWT payload
            now = datetime.now(timezone.utc)
            payload = {
                'iat': now.isoformat(),  # Issued at
                'exp': (now + timedelta(minutes=5)).isoformat(),  # Expires in 5 minutes
                'jti': str(uuid.uuid4())  # JWT ID (using a new UUID)
            }

            # Prepare headers
            headers = {
                'alg': 'ES256',
                'typ': 'JWT',
                'opr': 'production',
                'device': serial_number
            }

            # Create JWT request
            jwt_request = {
                'headers': headers,
                'barn': payload,
                'expires_in': 5
            }

            url = f"{self.web_base_url}/api/jwt/create"
            logger.debug(f"Creating JWT token at: {url}")
            logger.debug(f"JWT Request payload: {json.dumps(jwt_request, indent=2)}")

            response = requests.post(url, json=jwt_request, timeout=10)
            response.raise_for_status()

            jwt_response = response.json()
            jwt_token = jwt_response.get('jwt')

            if not jwt_token:
                raise ValueError("No JWT token in response")

            logger.info("JWT token created successfully")
            logger.debug(f"JWT Token (for debugging): {jwt_token}")
            return jwt_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error creating JWT token: {e}")
            raise e

    def setup_jwt_authentication(self):
        """Set up JWT authentication for MQTT"""
        try:
            # Get crypto info to retrieve serialNumber
            crypto_info = self.get_crypto_info()
            serial_number = crypto_info.get('serialNumber')
            
            if not serial_number:
                raise ValueError("No serialNumber found in crypto info")
            
            # Create JWT token
            jwt_token = self.create_jwt_token()
            
            # Set MQTT credentials: deviceid and username are serialNumber, password is JWT
            self.client_id = serial_number
            self.device_id = serial_number
            
            # Set the state topic using device_id
            self.state_topic = f"device/{self.device_id}/state"
            
            self.client.username_pw_set(serial_number, jwt_token)
            
            logger.info(f"JWT authentication set up for client: {serial_number}")
            
        except Exception as e:
            logger.error(f"Failed to set up JWT authentication: {e}")
            raise e

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
                logger.info("Published gateway state successfully")
                logger.debug(f"Gateway state payload: {payload}")
            else:
                logger.error(f"Failed to publish gateway state, error code: {result.rc}")

        except Exception as e:
            logger.error(f"Error publishing gateway state: {e}")

    def connect(self):
        """Connect to MQTT broker"""
        try:
            # Setup JWT authentication
            self.setup_jwt_authentication()

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

        # Wait for connection to establish
        time.sleep(2)

        # Main loop - publish gateway state every minute
        try:
            while self.running:
                # Fetch and publish gateway state every 60 seconds
                state_data = self.fetch_gateway_state()
                self.publish_state(state_data)

                # Wait for 60 seconds or until interrupted
                for _ in range(60):
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
