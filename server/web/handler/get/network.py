import json
from server.wifi.wifi import get_connection_configs, is_connected, get_ip_address
from ..handler import GetHandler
from ..requestData import RequestData
import logging
import ipaddress
import socket

logger = logging.getLogger(__name__)

class NetworkHandler(GetHandler):
    def schema(self):
        return self.create_schema(
            "Returns the list of networks",
            returns={"connections": "list of dicts, containing the configured networks."}
        )

    def do_get(self, data: RequestData):
        return 200, json.dumps({"connections": get_connection_configs()})


class AddressHandler(GetHandler):
    def schema(self):
        return self.create_schema(
            "Returns the IP address of the device",
            returns={"ip": "string, containing the IP local network address of the device. 127.0.0.1 is returned if no network is available.",
                     "port": "int, containing the port of the REST server."}
        )

    def do_get(self, data: RequestData):
        if is_connected():
            return 200, json.dumps({"ip": get_ip_address(), "port": data.bb.rest_server_port})
        else:
            return 200, json.dumps({"ip": "no network", "port": 0})


# A class to scan for modbus devices on the network
class ModbusScanHandler(GetHandler):
    def schema(self):
        return {
            "description": "Scans the network for modbus devices",
            "optional": {
                "ports": "string, containing a comma separated list of ports to scan for modbus devices.",
                "timeout": "float, the timeout in seconds for each ip:port scan. Default is 0.01 (10ms)."
            },
            "returns": {
                "devices": "a list of JSON Objects: {'host': host ip, 'port': host port}."
                }
        }

    def parse_ports(self, ports_str):
        """Parse a string of ports and port ranges into a list of integers."""
        ports = []
        for part in ports_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(part))
        return ports

    def scan_ip(self, ip: str, port: int, timeout: float):
        """Check if a specific port is open on a given IP address."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except socket.error:
            return False
        
    def scan_ports(self, ports: list[int], timeout: float):
        """Scan the local network for modbus devices on the given ports."""
        
        local_ip = get_ip_address()
        # Extract the network prefix from the local IP address
        network_prefix = ".".join(local_ip.split(".")[:-1]) + ".0/24"
        subnet = ipaddress.ip_network(network_prefix)
        
        logger.info(f"Scanning subnet {subnet} for modbus devices on ports {ports} with timeout {timeout}.")
        
        modbus_devices = []

        for ip in subnet.hosts():
            ip = str(ip)
            for port in ports:
                if self.scan_ip(ip, port, float(timeout)):
                    device = {
                        "ip": ip,
                        "port": port
                    }
                    modbus_devices.append(device)

        if not modbus_devices:
            logger.info(f"No IPs with given port(s) {ports} open found in the subnet {subnet}")

        return modbus_devices


    def do_get(self, data: RequestData):
        """Scan the network for modbus devices."""
        
        ports = data.query_params.get("ports", "502,1502,6607")
        ports = self.parse_ports(ports)
        timeout = data.query_params.get("timeout", 0.01) # 10ms may be too short for some networks? 

        modbus_devices = self.scan_ports(ports=ports, timeout=timeout)
    
        return 200, json.dumps({"devices":modbus_devices})

