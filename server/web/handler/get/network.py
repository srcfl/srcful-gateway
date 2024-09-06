import json
from server.network.wifi import get_connection_configs, is_connected, get_ip_address, get_ip_addresses_with_interfaces
from server.network import macAddr
from ..handler import GetHandler
from ..requestData import RequestData
import logging
import ipaddress
import socket

logger = logging.getLogger(__name__)

class NetworkHandler(GetHandler):
    @property
    def CONNECTIONS(self):
        return "connections"

    def schema(self):
        return self.create_schema(
            "Returns the list of networks",
            returns={self.CONNECTIONS: "list of dicts, containing the configured networks."}
        )

    def do_get(self, data: RequestData):
        return 200, json.dumps({self.CONNECTIONS: get_connection_configs()})


class AddressHandler(GetHandler):


    @property
    def IP(self):
        return "ip"
    
    @property
    def PORT(self):
        return "port"
    
    @property
    def ETH0_MAC(self):
        return "eth0_mac"
    
    @property
    def WLAN0_MAC(self):
        return "wlan0_mac"
    
    @property
    def NA(self):
        return "n/a"
    
    @property
    def INTERFACES(self):
        return "interfaces"

    def schema(self):
        return self.create_schema(
            "Returns the IP address of the device",
            returns={self.IP: "string, containing the IP local network address of the device. 127.0.0.1 is returned if no network is available.",
                     self.PORT: "int, containing the port of the REST server.",
                     self.ETH0_MAC: f"string, the mac adress of the first ethernet adapter or {self.NA} if not available",
                     self.WLAN0_MAC: f"string, the mac adress of the first wifi adapter or {self.NA} if not available",
                     self.INTERFACES: f"dictionary, interface and ip adress pairs, typically starts with en - for ethernet or wl for wifi (wlan)",
                    }
        )

    def do_get(self, data: RequestData):

        ip = get_ip_address() if is_connected() else "no network"
        ip_interfaces = get_ip_addresses_with_interfaces()
        
        try:
            wlan0 = macAddr.get_wlan0()
        except Exception:
            wlan0 = self.NA

        try:
            eth0 = macAddr.get_eth0()
        except Exception:
            eth0 = self.NA

        response = {
            self.IP: ip,
            self.PORT: data.bb.rest_server_port,
            self.ETH0_MAC: eth0,
            self.WLAN0_MAC: wlan0,
            self.INTERFACES : {iface: ip for iface, ip in ip_interfaces}
        }
        return 200, json.dumps(response)


# A class to scan for modbus devices on the network
class ModbusScanHandler(GetHandler):

    @property
    def IP(self) -> str:
        return "ip"
    
    @property
    def PORT(self) -> str:
        return "port"

    @property
    def DEVICES(self) -> str:
        return "devices"
    
    @property
    def PORTS(self) -> str:
        return "ports"
    
    @property
    def TIMEOUT(self) -> str:
        return "timeout"

    def schema(self) -> dict:
        return {
            "description": "Scans the network for modbus devices",
            "optional": {
                self.PORTS: "string, containing a comma separated list of ports to scan for modbus devices.",
                self.TIMEOUT: "float, the timeout in seconds for each ip:port scan. Default is 0.01 (10ms)."
            },
            "returns": {
                self.DEVICES: "a list of JSON Objects: {'host': host ip, 'port': host port}."
                }
        }

    def parse_ports(self, ports_str) -> list[int]:
        """Parse a string of ports and port ranges into a list of integers."""
        ports = []
        for part in ports_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(part))
        return ports

    def scan_ip(self, ip: str, port: int, timeout: float) -> bool:
        """Check if a specific port is open on a given IP address."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)

            sock.connect((ip, port))
            sock.close()
            return True
        except socket.error:
            return False
        
    def scan_ports(self, ports: list[int], timeout: float) -> list[dict[str, str]]:
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
                        self.IP: ip,
                        self.PORT: port
                    }
                    modbus_devices.append(device)

        if not modbus_devices:
            logger.info(f"No IPs with given port(s) {ports} open found in the subnet {subnet}")

        return modbus_devices


    def do_get(self, data: RequestData):
        """Scan the network for modbus devices."""
        
        ports = data.query_params.get(self.PORTS, "502,1502,6607,8899")
        ports = self.parse_ports(ports)
        timeout = data.query_params.get(self.TIMEOUT, 0.01) # 10ms may be too short for some networks? 

        modbus_devices = self.scan_ports(ports=ports, timeout=timeout)
        
        return 200, json.dumps({self.DEVICES:modbus_devices})

