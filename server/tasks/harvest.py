
import logging
import requests
from server.app.blackboard import BlackBoard
from server.devices.ICom import ICom
from server.devices.supported_devices.data_models import DERData, PVData, BatteryData, MeterData, Value
from typing import List

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

def post_to_mqtt_service(data, device_sn):
    response = requests.post(
        "http://localhost:8090/publish",
        json=data,
        timeout=2,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        logger.debug(f"Published harvest data to MQTT for device {device_sn}")
    else:
        logger.warning(f"Failed to publish harvest data: {response.status_code}")

def publish_to_mqtt(timestamp: int, device_id: str, device_sn: str, der_data: DERData):
    data = {
        "topic": f"sourceful/{device_id}/harvest",
        "payload": {
            "timestamp": timestamp,
            "device_sn": device_sn,
            "channels": der_data.to_dict()
        }
    }

    post_to_mqtt_service(data, device_sn)

    # Publish to individual channel data to separate MQTT topics
    ders: List[PVData | BatteryData | MeterData] = der_data.get_ders()
    for der in ders:
        for channel, value in der.to_dict().items():
            data = {
                "topic": f"sourceful/{device_id}/{der.name}/{device_sn}/{channel}",
                "payload": value
            }
            post_to_mqtt_service(data, device_sn)


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

                decoded_harvest = device.dict_to_ders(harvest)

                # Simple POST to MQTT container
                publish_to_mqtt(end_time, device_id, device_sn, decoded_harvest)

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