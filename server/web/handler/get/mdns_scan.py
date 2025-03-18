# A class to scan for modbus devices on the network
import logging
import json
from ..handler import GetHandler
from ..requestData import RequestData
from server.tasks.discover_mdns_devices_task import DiscoverMdnsDevicesTask
from server.devices.ICom import ICom
from typing import List

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MdnsScanHandler(GetHandler):

    @property
    def DEVICES(self) -> str:
        return "devices"

    def schema(self) -> dict:
        return {
            "description": "Scans the network for mdns devices",
            "returns": {
                self.DEVICES: "a list of JSON Objects: {'host': host ip, 'port': host port}."
            }
        }

    def do_get(self, data: RequestData):
        """Scan the network for modbus and P1 devices."""

        mdns_task = DiscoverMdnsDevicesTask(event_time=0, bb=data.bb)

        devices: List[ICom] = mdns_task.discover_mdns_devices()

        return 200, json.dumps([device.get_config() for device in devices])
