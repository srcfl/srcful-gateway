# A class to scan for modbus devices on the network
import logging
import json

from server.devices.inverters.ModbusTCP import ModbusTCP
from server.tasks.discoverModbusDevicesTask import DiscoverModbusDevicesTask
from ..handler import GetHandler
from ..requestData import RequestData
from server.network.network_utils import NetworkUtils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ModbusScanHandler(GetHandler):

    @property
    def DEVICES(self) -> str:
        return "devices"
    
    def schema(self) -> dict:
        return {
            "description": "Scans the network for modbus devices",
            "optional": {
                NetworkUtils.PORTS_KEY: "string, containing a comma separated list of ports to scan for modbus devices.",
                NetworkUtils.TIMEOUT_KEY: "float, the timeout in seconds for each ip:port scan. Default is 0.01 (10ms)."
            },
            "returns": {
                self.DEVICES: "a list of JSON Objects: {'host': host ip, 'port': host port}."
                }
        }

    def do_get(self, data: RequestData):
        """Scan the network for modbus devices."""
        
        ports = data.query_params.get(NetworkUtils.PORTS_KEY, "502,1502,6607,8899")
        ports = NetworkUtils.parse_ports(ports)
        timeout = data.query_params.get(NetworkUtils.TIMEOUT_KEY, 0.01) # 10ms may be too short for some networks?

        available_devices = NetworkUtils.get_hosts(ports=ports, timeout=timeout)
        
        # call discover modbus devices task
        task = DiscoverModbusDevicesTask(event_time=data.bb.time_ms() + 1000, bb=data.bb)
        data.bb.add_task(task)
    
        return 200, json.dumps({"status": "Scanning for modbus devices"})
