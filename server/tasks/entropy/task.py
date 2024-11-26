from datetime import datetime, timedelta, timezone
import logging
import threading
import time
import requests
from server.app.blackboard import BlackBoard
from server.app.settings.settings_observable import ChangeSource
import server.crypto.crypto as crypto
import server.crypto.revive_run as revive_run
import random
import math
import tempfile

from server.app.settings.settings import Settings
from server.tasks.entropy.settings import EntropySettings

from ..task import Task
from ..getSettingsTask import create_query_json as create_settings_query_json
from typing import Dict, List, Optional
import paho.mqtt.client as mqtt
import ssl
import json
import os

import server.backend as backend

logger = logging.getLogger(__name__)

_LAST_INSTANCE_ID = 0


def register_entropy_settings_listener(bb:BlackBoard):

    def on_do_mine_change(source:ChangeSource):
        if bb.settings.entropy.do_mine:
            logger.info("Starting entropy task")
            bb.add_task(EntropyTask(bb.time_ms() + generate_poisson_delay(), bb))

    bb.settings.entropy.add_listener(on_do_mine_change)

def generate_poisson_delay():
    AVERAGE_DELAY_MINUTES = 60
    """Generate exponentially distributed delay"""
    
    #ensure U is not 0 as log(0) is undefined
    U = 0
    while U <= 0:
        U = random.random()

    delay_minutes = -AVERAGE_DELAY_MINUTES * math.log(U)
    return 1000 * 60
    # return int(delay_minutes * 60 * 1000)

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
    
            
    def _create_entropy_data(self) -> Dict[str, int | str]:
        with crypto.Chip() as chip:
            entropy = generate_entropy(chip)
            serial = chip.get_serial_number().hex()
            timestamp_sec = self.bb.time_ms() // 1000
            signature = chip.get_signature(str(entropy) + serial + str(timestamp_sec)).hex()
        return {"entropy": entropy, "serial": serial, "sig": signature, "timestamp_sec": timestamp_sec}


    def create_ssl_context(self, cert_string, key_string):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        context.minimum_version = ssl.TLSVersion.TLSv1_2  # Enforce minimum TLS version
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # Disable older TLS versions
        context.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256')  # Set strong ciphers
        
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

    def _setup_mqtt(self, cert_pem, cert_private_key, config:EntropySettings) -> mqtt.Client:

        client_id = f"gateway-{random.randint(0, 1000000)}"
        mqtt_client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

        # Use an event to track MQTT protocol connection
        mqtt_connected = threading.Event()

        # Add logging callbacks
        def on_connect(client, userdata, flags, rc):
            logger.debug(f"MQTT Connect result: {rc}")
            if rc == 0:
                mqtt_connected.set()
            else:
                logger.error(f"Connection failed with code {rc}")
                # Reference: https://github.com/eclipse/paho.mqtt.python/blob/master/src/paho/mqtt/client.py#L49
                codes = {
                    1: "incorrect protocol version",
                    2: "invalid client identifier",
                    3: "server unavailable",
                    4: "bad username or password",
                    5: "not authorised",
                }
                logger.error(f"Error message: {codes.get(rc, 'unknown error')}")

        def on_log(client, userdata, level, buf):
            logger.debug(f"MQTT Log: {buf}")

        def on_disconnect(client, userdata, rc):
            logger.info(f"MQTT Disconnected with result code: {rc}")

        def on_publish(client, userdata, mid):
            logger.info(f"Message {mid} published successfully")

        def on_log(client, userdata, level, buf):
            logger.debug(f"MQTT Log: {buf}")

        def on_connect_fail(client, rc):
            logger.error(f"MQTT Connect failed with result code: {rc}")
            logger.error(f"Failed to connect to MQTT broker with error code {rc}: {mqtt.connack_string(rc)}")

        mqtt_client.on_connect_fail = on_connect_fail
        mqtt_client.on_connect = on_connect
        mqtt_client.on_disconnect = on_disconnect
        mqtt_client.on_publish = on_publish
        mqtt_client.on_log = on_log


        # Set up TLS with in-memory certificates
        ssl_context = self.create_ssl_context(cert_pem, cert_private_key)
 
        mqtt_client.tls_set_context(ssl_context)

        mqtt_client.loop_start()

        # Connect to the broker
        logger.debug(f"Connecting to MQTT broker {config.mqtt_broker}:{config.mqtt_port}")
        rc = mqtt_client.connect(config.mqtt_broker, config.mqtt_port)
        if rc != mqtt.MQTTErrorCode.MQTT_ERR_SUCCESS:
            mqtt_client.loop_stop()
            raise Exception(f"Failed to connect to MQTT broker with error code {rc}: {mqtt.connack_string(rc)}")
        if not mqtt_connected.wait(timeout=5.0):
            mqtt_client.loop_stop()
            raise Exception("MQTT protocol connection timeout")

        logger.debug("MQTT connection fully established")

        return mqtt_client

    def _publish_entropy(self, client:mqtt.Client, entropy_data:dict, config:EntropySettings):
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
            logger.info("Published entropy: %s", entropy_data)
            self.adjust_time(self.bb.time_ms() + generate_poisson_delay())
            self.bb.add_info("Generating Entropy...")
        except Exception as e:
            logger.error(f"Failed to publish entropy: {e}")
            self.adjust_time(self.bb.time_ms() + 60000)

        client.disconnect()
        
    
    def _get_cert_and_key(self):
        unix_timestamp = int(time.time())

        dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)

        # Format datetime as ISO 8601 string
        # should be something like 2024-08-26T13:02:00
        iso_timestamp = dt.isoformat().replace('+00:00', '')

        with crypto.Chip() as chip:
            serial = chip.get_serial_number().hex()
            timestamp = iso_timestamp
            message = f"{serial}|{timestamp}"
            signature = chip.get_signature(message).hex()
        
        gateway = backend.Gateway(serial)

        try:
            # TODO: remove this endpoint and use the one from the settings
            certs = gateway.get_globals(backend.Connection("https://api-test.srcful.dev/", 5), timestamp, signature, "entropy_certs")
            cert_pem = certs["cert_pem"]
            cert_private_key = certs["cert_private_key"]
            return cert_pem, cert_private_key
        except Exception as e:
            logger.error("Failed to get certificate and key: %s", e)
            raise e

        raise Exception("Failed to get certificate and key") 

    def _has_mined_srcful_data(self, serial:str) -> bool:
        # check the DERs of the gateway and get the last 24h of data
        # if there is any data return true
        # otherwise return false

        gateway = backend.Gateway(serial)
        connection = backend.Connection(self.bb.settings.api.gql_endpoint, self.bb.settings.api.gql_timeout)
        ders:List[backend.DER] = gateway.get_ders(connection)
        resolution = backend.Histogram.Resolution(backend.Histogram.Resolution.Type.HOUR, 1)

        for der in ders:
            histogram = der.histogram_from_now(connection, timedelta(hours=24), resolution)
            if len(histogram) > 0:
                return True

        return False
    
    def execute(self, event_time):
        if self.instance_id != _LAST_INSTANCE_ID:
            logger.info(f"Running version {self.instance_id} is not the last instance id {_LAST_INSTANCE_ID}, Terminating")
            return None
        
        if self.bb.settings.entropy.do_mine:
            if not self._has_mined_srcful_data(self.bb.crypto_state().serial_number.hex()):
                logger.info("No srcful data mined in 24h, skipping entropy, better luck next hour")
                self.adjust_time(self.bb.time_ms() + 60000)
                return self
            
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