import logging
import requests
from server.inverters.supported_inverters.profiles import InverterProfile
from server.inverters.der import DER
from server.inverters.modbus import Modbus
from server.blackboard import BlackBoard
import server.crypto.crypto as crypto
import server.crypto.revive_run as revive_run
import random
import math
import tempfile


from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend

from server.settings import Settings

from .srcfulAPICallTask import SrcfulAPICallTask
from .task import Task
from .getSettingsTask import create_query_json as create_settings_query_json
from typing import Optional
import paho.mqtt.client as mqtt
import ssl
import json
import os

logger = logging.getLogger(__name__)

_LAST_INSTANCE_ID = 0

def generate_poisson_delay():
    AVERAGE_DELAY_MINUTES = 60
    """Generate exponentially distributed delay"""
    
    #ensure U is not 0 as log(0) is undefined
    U = 0
    while U <= 0:
        U = random.random()

    delay_minutes = -AVERAGE_DELAY_MINUTES * math.log(U)
    # return 5000
    return int(delay_minutes * 60 * 1000)

def generate_entropy(chip: crypto.Chip):
        random_bytes = chip.get_random()
        random_int = int.from_bytes(random_bytes, byteorder='big')

        # get the last 64 bits
        return random_int & 0xFFFFFFFFFFFFFFFF

class EntropyTask(Task):
    do_increase_chip_death_count = True  # prevents excessive incrementing of chip death count

    @property
    def SUBKEY(self):
        return "entropy"

    def __init__(self, event_time: int, bb: BlackBoard):
        global _LAST_INSTANCE_ID
        super().__init__(event_time, bb)
        self.cert_pem = None
        self.cert_private_key = None
        _LAST_INSTANCE_ID = _LAST_INSTANCE_ID + 1
        self.instance_id = _LAST_INSTANCE_ID
    
            
    def _create_entropy_data(self):
        with crypto.Chip() as chip:
            entropy = generate_entropy(chip)
        return {"entropy": entropy}


    def create_ssl_context(self, cert_string, key_string):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Create temporary files for the certificate and key
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as cert_file, \
            tempfile.NamedTemporaryFile(mode='w', delete=False) as key_file:
        
            cert_file.write(cert_string)
            key_file.write(key_string)
        
            # Ensure the data is written to the files
            cert_file.flush()
            key_file.flush()
        
            # Get the file paths
            cert_path = cert_file.name
            key_path = key_file.name
    
        try:
            # Load the certificate chain from the temporary files
            context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        finally:
            # Clean up the temporary files
            os.unlink(cert_path)
            os.unlink(key_path)
        
        return context

    def _setup_mqtt(self, cert_pem, cert_private_key, config:Settings.Entropy) -> mqtt.Client:

        mqtt_client = mqtt.Client()

        # Set up TLS with in-memory certificates
        ssl_context = self.create_ssl_context(cert_pem, cert_private_key)
 
        mqtt_client.tls_set_context(ssl_context)

        # Connect to the broker
        logger.debug(f"Connecting to MQTT broker {config.mqtt_broker}:{config.mqtt_port}")
        mqtt_client.connect(config.mqtt_broker, config.mqtt_port)
        mqtt_client.loop_start()

        return mqtt_client

    def _publish_entropy(self, client:mqtt.Client, entropy_data:dict, config:Settings.Entropy):
        payload = json.dumps(entropy_data)
        response:mqtt.MQTTMessageInfo = client.publish(config.mqtt_topic, payload)

        response.wait_for_publish(60)
        
    
    def send_entropy(self, entropy_data:dict, cert_pem, cert_private_key):
        try:
            client = self._setup_mqtt(cert_pem, cert_private_key, self.bb.settings.entropy)
        except Exception as e:
            logger.error(f"Failed to set up MQTT client: {e}")
            self.adjust_time(self.bb.time_ms() + 60000)
            return 
        
        try:
            self._publish_entropy(client, entropy_data, self.bb.settings.entropy)
            self.adjust_time(self.bb.time_ms() + generate_poisson_delay())
            self.bb.add_info("Generating Entropy...")
        except Exception as e:
            logger.error(f"Failed to publish entropy: {e}")
            self.adjust_time(self.bb.time_ms() + 60000)

        client.disconnect()
        
    
    def _get_cert_and_key(self):
        with crypto.Chip() as chip:
            q = create_settings_query_json(chip, self.SUBKEY)

        res = requests.post(self.bb.settings.api.gql_endpoint, json=q, timeout=self.bb.settings.api.gql_timeout)

        if res.status_code == 200:
            data = res.json()

            entropy_cert_data = data.get("data",{}).get("gatewayConfiguration", {}).get("configuration", {}).get("data", {})
            entropy_cert_data = json.loads(entropy_cert_data)
            logger.info(f"entropy cert: {entropy_cert_data}")

            if 'cert_pem' in entropy_cert_data and 'cert_private_key' in entropy_cert_data:
                return entropy_cert_data["cert_pem"], entropy_cert_data["cert_private_key"]
        
        raise Exception("Failed to get certificate and key") 
        
    
    def execute(self, event_time):
        if self.instance_id != _LAST_INSTANCE_ID:
            logger.info(f"Running version {self.instance_id} is not the last instance id {_LAST_INSTANCE_ID}, Terminating")
            return None
        
        if self.bb.settings.entropy.do_mine:
            if self.cert_pem is None or self.cert_private_key is None:
                # fetch the cert and key from the settings with subkey entropy
                try:
                    self.cert_pem, self.cert_private_key = self._get_cert_and_key()
                except Exception as e:
                    logger.error("Error fetching certificate and key: %s", e)
                    # retry in 60 seconds
                    self.adjust_time(self.bb.time_ms() + 60000)
                    return [self]
            
            # this sends and sets a new time for rescheduling.
            self.send_entropy(self._get_entropy_data(), self.cert_pem, self.cert_private_key)
            
            return self
        else:
            return None

    def _get_entropy_data(self):
        retries = 5
        exception = None
    
        while retries > 0:
            try:
                entropy_data = self._create_entropy_data()
                return entropy_data
            except crypto.ChipError as e:
                exception = e
                if retries > 0:
                    retries -= 1
                    revive_run.as_process()
                
            except Exception as e:
                exception = e
                logger.error("Error creating Entrophy JWT: %s", e)

        # if we end up here the chip has not been revived        
        if EntropyTask.do_increase_chip_death_count:
            self.bb.increment_chip_death_count()
            EntropyTask.do_increase_chip_death_count = False
        logger.info("Incrementing chip death count to: %i ", self.bb.chip_death_count)
        raise exception