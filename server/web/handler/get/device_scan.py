# A class to scan for modbus devices on the network
import logging
import json
from ..handler import GetHandler
from ..requestData import RequestData
from server.network.network_utils import NetworkUtils
from server.tasks.discoverDevicesTask import DiscoverDevicesTask
from server.devices.ICom import ICom
from typing import List

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DeviceScanHandler(GetHandler):

    @property
    def DEVICES(self) -> str:
        return "devices"
    
    def schema(self) -> dict:
        return {
            "description": "Scans the network for modbus devices",
            "optional": {
                NetworkUtils.PORTS_KEY: "string, containing a comma separated list of ports to scan for modbus devices.",
                NetworkUtils.TIMEOUT_KEY: f"float, the timeout in seconds for each ip:port scan. Default is {NetworkUtils.DEFAULT_TIMEOUT} second(s)."
            },
            "returns": {
                self.DEVICES: "a list of JSON Objects: {'host': host ip, 'port': host port}."
                }
        }

    def do_get(self, data: RequestData):
        """Scan the network for modbus and P1 devices."""
        
        scan_task = DiscoverDevicesTask(event_time=0, bb=data.bb)
        
        ports_str = data.query_params.get(NetworkUtils.PORTS_KEY, NetworkUtils.DEFAULT_MODBUS_PORTS)
        timeout = data.query_params.get(NetworkUtils.TIMEOUT_KEY, NetworkUtils.DEFAULT_TIMEOUT) 
        
        devices: List[ICom] = scan_task.discover_devices(ports_str=ports_str, timeout=timeout)
        
        return 200, json.dumps([device.get_config() for device in devices])