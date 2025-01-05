import logging
import json
from ..handler import GetHandler
from ..requestData import RequestData
from server.network.network_utils import NetworkUtils, HostInfo
from typing import List

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class NetworkScanHandler(GetHandler):
    
    def schema(self):
        return self.create_schema(
            "Scans the network for devices",
            returns={"hosts": "a list of JSON Objects: {'host': host ip, 'port': host port, 'mac': host mac}."}
        )
        
    def do_get(self, data: RequestData):
        """Scan the network for devices"""
        
        logger.info(f"Scanning the network for devices")
        
        ports = data.query_params.get(NetworkUtils.PORTS_KEY, NetworkUtils.DEFAULT_MODBUS_PORTS)
        timeout = data.query_params.get(NetworkUtils.TIMEOUT_KEY, NetworkUtils.DEFAULT_TIMEOUT)
        
        ports = NetworkUtils.parse_ports(ports)
        
        logger.info(f"Scanning the network for devices with ports: {ports} and timeout: {timeout}")
        
        hosts: List[HostInfo] = NetworkUtils.get_hosts(ports=ports, timeout=timeout)
        
        return 200, json.dumps([dict(host) for host in hosts])