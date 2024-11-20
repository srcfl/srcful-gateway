import logging
import time
from datetime import datetime, timezone
from typing import List, Union, Tuple
import requests
from .itask import ITask
import server.crypto.crypto as crypto
from server.app.blackboard import BlackBoard
from .srcfulAPICallTask import SrcfulAPICallTask
from server.app.settings.settings_observable import ChangeSource
from server.tasks.saveSettingsTask import SaveSettingsTask
import json


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


def handle_settings(bb: BlackBoard, raw_json_data_from_api: dict):
    logger.info("Got settings: %s", raw_json_data_from_api)

    try:
        
        if raw_json_data_from_api is not None and raw_json_data_from_api["data"] is not None:
            logger.info("Updating settings: %s", raw_json_data_from_api)
            bb.settings.update_from_dict(json.loads(raw_json_data_from_api["data"]), ChangeSource.BACKEND)
        else:
            logger.error("Settings are None")
            # save the default settings
            return SaveSettingsTask(1017, bb)
    except KeyError:
        logger.error("Wrong json format: %s", raw_json_data_from_api)
        return None
    except TypeError:
        logger.error("Wrong json format: %s", raw_json_data_from_api)
        return None

def create_query_json(chip: crypto.Chip, subkey: str):
    unix_timestamp = int(time.time())

    dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)

    # Format datetime as ISO 8601 string
    # should be something like 2024-08-26T13:02:00
    iso_timestamp = dt.isoformat().replace('+00:00', '')

    serial = chip.get_serial_number().hex()
    timestamp = iso_timestamp
    message = f"{serial}:{timestamp}"
    signature = chip.get_signature(message).hex()

    q = """
        {
            gatewayConfiguration {
                configuration(deviceAuth: {
                    id: $serial,
                    timestamp: $timestamp,
                    signedIdAndTimestamp: $signature,
                    subKey: $subKey
                }) {
                data
                }
            }
        }
    """

    q = q.replace("$timestamp", f'"{timestamp}"')
    q = q.replace("$serial", f'"{serial}"')
    q = q.replace("$signature", f'"{signature}"')
    q = q.replace("$subKey", f'"{subkey}"')

    return {"query": q}


class GetSettingsTask(SrcfulAPICallTask):
    """Task to get the configuration from the server using the crypto chip"""

    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        self.settings = None
        self.post_url = "https://api.srcful.dev/"

    def _json(self):
        with crypto.Chip() as chip:
            query = create_query_json(chip, self.bb.settings.API_SUBKEY)
        return query
        


    def _on_error(self, reply: requests.Response) -> Union[int, Tuple[int, Union[List[ITask], ITask, None]]]:
        return 0

    def _on_200(self, reply: requests.Response) -> Union[List[ITask], ITask, None]:
        json_data = reply.json()
        return handle_settings(self.bb, json_data["data"]["gatewayConfiguration"]["configuration"])
        
    
