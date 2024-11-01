from dataclasses import dataclass
import logging
from typing import Optional
import socket
import ipaddress
from server.network.wifi import get_ip_address
from furl import furl

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class HostInfo:
    ip: str
    port: int
    mac: str


class NetworkUtils:
    """
    Utility class for network-related operations.
    """

    IP_KEY = 'ip'
    PORT_KEY = 'port'
    PORTS_KEY = 'ports'
    MAC_KEY = 'mac'
    HW_KEY = 'hw'
    FLAGS_KEY = 'flags'
    MASK_KEY = 'mask'
    DEVICE_KEY = 'device'
    TIMEOUT_KEY = 'timeout'
    DEFAULT_MODBUS_PORTS = "502,6607,8899"
    DEFAULT_TIMEOUT = 0.1

    INVALID_MAC = "00:00:00:00:00:00"

    def __init__(self):
        raise NotImplementedError("This class shouldn't be instantiated.")
    
    @staticmethod
    def extract_ip(url: str) -> Optional[str]:
        """
        Extract IP address from a URL or IP string.
        Returns the IP if valid, None if invalid.
        
        Args:
            url (str): URL or IP address string
            
        Returns:
            Optional[str]: IP address or None if invalid
            
        Examples:
            >>> extract_ip("192.168.1.1")
            "192.168.1.1"
            >>> extract_ip("http://192.168.1.1")
            "192.168.1.1"
            >>> extract_ip("https://192.168.1.1:8080")
            "192.168.1.1"
        """
        parsed_url = NetworkUtils.parse_address(url)
        if not parsed_url:
            return None
            
        try:
            f = furl(parsed_url)
            ip = f.host
            # Validate it's a valid IP
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            return None
    
    @staticmethod
    def parse_address(url: str) -> Optional[str]:
        """
        Parse URL and validate it contains an IP address (not a hostname).
        Returns URL if valid, None if invalid.
        
        Args:
            url (str): URL or IP address
            
        Returns:
            Optional[str]: URL or None if invalid
        """
        try:
            # If it's just an IP, convert it to a URL
            try:
                ipaddress.ip_address(url)
                f = furl(scheme='http', host=url)
            except ValueError:
                f = furl(url)

            # Validate the host is an IP address
            if not f.host:
                return None
                
            ipaddress.ip_address(f.host)
            return str(f)

        except ValueError:
            return None

    # Method to get the arp table   
    @staticmethod
    def arp_table() -> list[dict[str, str]]:
        """Refresh the ARP table from the system."""
        logger.info("Scanning ARP table")
        try:
            with open('/proc/net/arp', 'r', encoding='utf-8') as f:
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
            return arp_table
        except FileNotFoundError:
            logger.warning("ARP table file not found. Using empty ARP table.")
            return []
        
    
    @staticmethod
    def get_mac_from_ip(ip: str) -> str:
        """Get the MAC address from the ARP table for a given IP address or URL."""
        ip = NetworkUtils.extract_ip(ip)
        for entry in NetworkUtils.arp_table():
            if entry[NetworkUtils.IP_KEY] == ip:
                return entry[NetworkUtils.MAC_KEY]
        return NetworkUtils.INVALID_MAC
    
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
    def get_hosts(ports: list[int], timeout: float) -> list[HostInfo]:
        """
        Scan the local network for modbus devices on the given ports.
        """
        local_ip = get_ip_address()
        
        try:
            local_ip = get_ip_address()
        except Exception as e:
            logger.error("Failed to get IP address: %s", str(e))
            return []

        if not local_ip:
            logger.warning("No active network connection found.")
            return []
        
        # Refresh the ARP table
        NetworkUtils.arp_table()
        
        # Extract the network prefix from the local IP address
        network_prefix = ".".join(local_ip.split(".")[:-1]) + ".0/24"
        subnet = ipaddress.ip_network(network_prefix)
        
        logger.info("Scanning subnet %s for modbus devices on ports %s with timeout %s", subnet, ports, timeout)
        
        ip_port_dict = []

        for ip in subnet.hosts():
            ip_str:str = str(ip)
            for port in ports:
                if NetworkUtils.is_port_open(ip_str, port, float(timeout)):
                    host_info = HostInfo(
                        ip=ip_str,
                        port=port,
                        mac=NetworkUtils.get_mac_from_ip(ip_str)
                    )
                    ip_port_dict.append(host_info)
        if not ip_port_dict:
            logger.info("No IPs with given port(s) %s open found in the subnet %s", ports, subnet)
            return []
        
        return ip_port_dict

