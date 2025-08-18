
import logging
import requests
from typing import List, Union
from server.tasks.itask import ITask
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.app.blackboard import BlackBoard
from .task import Task
from .harvestTransport import ITransportFactory
from server.devices.ICom import ICom
# get c´rypto 
from server.crypto.crypto_state import CryptoState

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class Harvest:
    def __init__(self):
        self.backoff_time = 1000  # start with a 1000ms backoff
        self.harvest_count = 0
        self.total_harvest_time_ms = 0

    def harvest(self, event_time:int, device: ICom, bb: BlackBoard) -> tuple[int, dict]:

        start_time = event_time
        elapsed_time_ms = 1000

        try:
            harvest = device.read_harvest_data(force_verbose=self.harvest_count % 10 == 0)
            self.harvest_count += 1
            end_time = bb.time_ms()

            elapsed_time_ms = end_time - start_time
            self.backoff_time = device.get_backoff_time_ms(elapsed_time_ms, self.backoff_time)
            logger.debug("Harvest from [%s] took %s ms. Data points: %s", device.get_SN(), elapsed_time_ms, len(harvest))

            self.total_harvest_time_ms += elapsed_time_ms

            # Publish harvest data to MQTT (non-blocking)
            try:
                device_sn = device.get_SN()
                device_id = bb.crypto_state().serial_number.hex()
                
                # Simple POST to MQTT container
                data = {
                    "topic": f"sourceful/device/{device_id}/harvest",
                    "payload": {
                        "type": "harvest",
                        "device_sn": device_sn,
                        "harvest_data": harvest,
                        "metadata": {
                            "harvest_count": self.harvest_count,
                            "elapsed_time_ms": elapsed_time_ms,
                            "backoff_time_ms": self.backoff_time,
                            "total_harvest_time_ms": self.total_harvest_time_ms
                        }
                    }
                }
                
                response = requests.post(
                    "http://localhost:8090/publish",  # Changed from 8080 to 8090
                    json=data,
                    timeout=2,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    logger.debug(f"Published harvest data to MQTT for device {device_sn}")
                else:
                    logger.warning(f"Failed to publish harvest data: {response.status_code}")
                    
            except Exception as mqtt_error:
                # Don't fail the harvest if MQTT publishing fails
                logger.error(f"Error publishing harvest data to MQTT: {mqtt_error}")

        except Exception as e:
            # To-Do: Solarmanv5 can raise ConnectionResetError, so handle it!
            raise ICom.ConnectionException("Error harvesting from device", device, e)

        # If we're reading faster than every 1000ms, we subtract the elapsed time of
        # the current harvest from the backoff time to keep polling at a constant rate of every 1000ms
        if elapsed_time_ms < self.backoff_time:
            next_time = bb.time_ms() + self.backoff_time - elapsed_time_ms
        else:
            next_time = bb.time_ms() + self.backoff_time

        return next_time, harvest    