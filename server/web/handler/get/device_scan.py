# A class to scan for modbus devices on the network
import logging
import json
from ..handler import GetHandler
from ..requestData import RequestData
from server.network.network_utils import NetworkUtils
from server.devices.inverters.modbus_device_scanner import scan_for_modbus_devices
from server.devices.p1meters.p1_scanner import scan_for_p1_devices
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
        
        ports = data.query_params.get(NetworkUtils.PORTS_KEY, NetworkUtils.DEFAULT_MODBUS_PORTS)
        ports = NetworkUtils.parse_ports(ports)

        # Scan for modbus devices
        devices:List[ICom] = scan_for_modbus_devices(ports=ports)
        
        # Scan for P1 devices
        p1_devices:List[ICom] = scan_for_p1_devices()
        
        # append p1 devices to the devices list
        devices.extend(p1_devices)
        
        logger.info(f"Found {len(devices)} devices")
        logger.info([device.get_config() for device in devices])
        
        data.bb.set_available_devices(devices=devices)

        return 200, json.dumps([device.get_config() for device in devices])