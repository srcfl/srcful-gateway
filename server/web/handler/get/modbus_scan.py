# A class to scan for modbus devices on the network
import logging
import json
from ..handler import GetHandler
from ..requestData import RequestData
from server.network.network_utils import NetworkUtils
from server.devices.inverters.ModbusTCP import ModbusTCP

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
                NetworkUtils.TIMEOUT_KEY: f"float, the timeout in seconds for each ip:port scan. Default is {NetworkUtils.DEFAULT_TIMEOUT} second(s)."
            },
            "returns": {
                self.DEVICES: "a list of JSON Objects: {'host': host ip, 'port': host port}."
                }
        }

    def do_get(self, data: RequestData):
        """Scan the network for modbus devices."""
        
        ports = data.query_params.get(NetworkUtils.PORTS_KEY, "502,1502,6607,8899")
        ports = NetworkUtils.parse_ports(ports)
        timeout = data.query_params.get(NetworkUtils.TIMEOUT_KEY, NetworkUtils.DEFAULT_TIMEOUT)
    
        hosts = NetworkUtils.get_hosts(ports=ports, timeout=timeout)
        
        icoms = []
        for host in hosts:
            args = {
                ModbusTCP.ip_key(): host.ip,
                ModbusTCP.port_key(): host.port,
                ModbusTCP.mac_key(): host.mac
            }
            
            icoms.append(ModbusTCP(**args))
        
        data.bb.set_available_devices(icoms)
        
        return 200, json.dumps([dict(host) for host in hosts])
