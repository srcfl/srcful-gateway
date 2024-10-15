import logging
import socket
import ipaddress
from server.network.wifi import get_ip_address
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NetworkUtils:
    
    _arp_table: Optional[list[dict[str, str, str, str, str, str]]] = None
    
    IP_KEY = 'ip'
    PORT_KEY = 'port'
    PORTS_KEY = 'ports'
    MAC_KEY = 'mac'
    HW_KEY = 'hw'
    FLAGS_KEY = 'flags'
    MASK_KEY = 'mask'
    DEVICE_KEY = 'device'
    TIMEOUT_KEY = 'timeout'
    DEFAULT_MODBUS_PORTS = "502,1502,6607,8899"
    DEFAULT_TIMEOUT = 0.01
    
    def __init__(self):
        raise NotImplementedError("This class shouldn't be instantiated.")

    
    # Method to get the arp table   
    @staticmethod
    def refresh_arp_table() -> None:
        logger.info("Scanning ARP table")
        try:
            with open('/proc/net/arp', 'r') as f:
                lines = f.readlines()[1:]  # Skip the header line
            
            arp_table = [
                dict(zip([NetworkUtils.IP_KEY, 
                          NetworkUtils.HW_KEY, 
                          NetworkUtils.FLAGS_KEY, 
                          NetworkUtils.MAC_KEY, 
                          NetworkUtils.MASK_KEY, 
                          NetworkUtils.DEVICE_KEY], line.split()))
                for line in lines
            ]
            NetworkUtils._arp_table = arp_table
        except FileNotFoundError:
            logger.warning("ARP table file not found. Using empty ARP table.")
            NetworkUtils._arp_table = []
        
    
    @staticmethod
    def get_mac_from_ip(ip: str) -> Optional[str]:
        if NetworkUtils._arp_table is None:
            NetworkUtils.refresh_arp_table()
        for entry in NetworkUtils._arp_table:
            if entry[NetworkUtils.IP_KEY] == ip:
                return entry[NetworkUtils.MAC_KEY]
        return None
    
    @staticmethod
    def parse_ports(ports_str: str) -> list[int]:
        """Parse a string of ports and port ranges into a list of integers."""
        ports = []
        for part in ports_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(part))
        return ports
    
    @staticmethod
    def is_port_open(ip: str, port: int, timeout: float) -> bool:
        """Check if a specific port is open on a given IP address."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)

            sock.connect((ip, port))
            sock.close()
            return True
        except socket.error:
            return False
        
    @staticmethod
    def get_hosts(ports: list[int], timeout: float) -> list[dict[str, str, str]]:
        """
        Scan the local network for modbus devices on the given ports.
        
        Returns a list of dictionaries with the IP, port, and MAC address of the devices in the format:
        [
            {
                NetworkUtils.IP_KEY: str,
                NetworkUtils.PORT_KEY: int,
                NetworkUtils.MAC_KEY: str
            },
            ...
        ]
        """
        
        local_ip = get_ip_address()
        # Refresh the ARP table
        NetworkUtils.refresh_arp_table()
        
        # Extract the network prefix from the local IP address
        network_prefix = ".".join(local_ip.split(".")[:-1]) + ".0/24"
        subnet = ipaddress.ip_network(network_prefix)
        
        logger.info(f"Scanning subnet {subnet} for modbus devices on ports {ports} with timeout {timeout}.")
        
        ip_port_dict = []

        for ip in subnet.hosts():
            ip = str(ip)
            for port in ports:
                if NetworkUtils.is_port_open(ip, port, float(timeout)):
                    ip_port = {
                        NetworkUtils.IP_KEY: ip,
                        NetworkUtils.PORT_KEY: port,
                        NetworkUtils.MAC_KEY: NetworkUtils.get_mac_from_ip(ip)
                    }
                    ip_port_dict.append(ip_port)

        if not ip_port_dict:
            logger.info(f"No IPs with given port(s) {ports} open found in the subnet {subnet}")
            return []
        
        return ip_port_dict