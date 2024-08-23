import requests
import logging
import time

from datetime import datetime, timezone

import server.crypto.crypto as crypto
from server.blackboard import BlackBoard

from .srcfulAPICallTask import SrcfulAPICallTask

log = logging.getLogger(__name__)


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
        iso_timestamp = dt.isoformat().replace('+00:00', 'Z')

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
                    subKey: "settings"
                    }) {
                    data
                    }
                }
            }
        """

        q = q.replace("$timestamp", f'"{timestamp}"')
        q = q.replace("$serial", f'"{serial}"')
        q = q.replace("$signature", f'"{signature}"')

        return {"query": q}


    def _on_error(self, reply: requests.Response) -> int:
        return 0

    def _on_200(self, reply: requests.Response):
        
        log.info("Got settings: %s", reply.json()["data"])
