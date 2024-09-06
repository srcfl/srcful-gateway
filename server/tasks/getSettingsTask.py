import requests
import logging
import time
from typing import List, Union, Tuple
from .itask import ITask

from datetime import datetime, timezone

import server.crypto.crypto as crypto
from server.blackboard import BlackBoard

from .srcfulAPICallTask import SrcfulAPICallTask
from server.settings import ChangeSource
log = logging.getLogger(__name__)

from server.tasks.saveSettingsTask import SaveSettingsTask

import json


def handle_settings(bb: BlackBoard, raw_json_data_from_api: dict):
    log.info("Got settings: %s", raw_json_data_from_api)

    try:
        
        if raw_json_data_from_api is not None and raw_json_data_from_api["data"] is not None:
            log.info("Updating settings: %s", raw_json_data_from_api)
            bb.settings.update_from_dict(json.loads(raw_json_data_from_api["data"]), ChangeSource.BACKEND)
        else:
            log.error("Settings are None")
            # save the default settings
            return SaveSettingsTask(1017, bb)
    except KeyError:
        log.error("Wrong json format: %s", raw_json_data_from_api)
        return None
    except TypeError:
        log.error("Wrong json format: %s", raw_json_data_from_api)
        return None

class GetSettingsTask(SrcfulAPICallTask):
    """Task to get the configuration from the server using the crypto chip"""

    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        self.settings = None
        self.post_url = "https://api.srcful.dev/"

    def _json(self):

        unix_timestamp = int(time.time())

        # Convert Unix timestamp to datetime object

        dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)

        # Format datetime as ISO 8601 string
        # should be something like 2024-08-26T13:02:00
        iso_timestamp = dt.isoformat().replace('+00:00', '')

        with crypto.Chip() as chip:
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
        q = q.replace("$subKey", f'"{self.bb.settings.API_SUBKEY}"')

        return {"query": q}


    def _on_error(self, reply: requests.Response) -> Union[int, Tuple[int, Union[List[ITask], ITask, None]]]:
        return 0

    def _on_200(self, reply: requests.Response) -> Union[List[ITask], ITask, None]:
        json_data = reply.json()
        return handle_settings(self.bb, json_data["data"]["gatewayConfiguration"]["configuration"])
        
    
