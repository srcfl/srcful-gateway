from server.devices.TCPDevice import TCPDevice
import logging
import requests
from server.network import mdns as mdns
from ..ICom import HarvestDataType, ICom
from typing import List, Optional
from server.network.network_utils import HostInfo, NetworkUtils
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger('charset_normalizer').setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Enphase(TCPDevice):
    """
    Enphase device class
    """

    CONNECTION = "ENPHASE"
    
    # Endpoint names
    PRODUCTION = "production"
    CONSUMPTION = "consumption"
    ENERGY = "energy"
    
    # Endpoint paths
    ENDPOINTS = {
        PRODUCTION: "/api/v1/production/inverters",
        CONSUMPTION: "/ivp/meters/reports/consumption",
        ENERGY: "/ivp/pdm/energy"
    }
    
    model_name: str
    
    @staticmethod
    def bearer_token_key():
        return "bearer_token"

    @staticmethod
    def get_supported_devices():
        return {Enphase.CONNECTION: {'device_type': 'enphase', 'display_name': 'Enphase', 'protocol': 'http'}}
    
    @staticmethod
    def get_config_schema():
        return {
            **TCPDevice.get_config_schema(),
            Enphase.bearer_token_key(): 'string, Bearer token for the device'

        }

    def __init__(self, **kwargs):
        
        self.bearer_token: str = kwargs.get(self.bearer_token_key(), None)
        
        if not self.bearer_token:
            raise ValueError("Bearer token is required")
        
        self.ip: str = kwargs.get(self.IP, None)
        self.ip = NetworkUtils.normalize_ip_url(self.ip) # 
        if not self.ip:
            raise ValueError("Base URL is required")

        TCPDevice.__init__(self, self.ip, kwargs.get(self.PORT, 80))
        
        self.headers: dict = {"Authorization": f"Bearer {self.bearer_token}"}
        
        self.session: requests.Session = None
        self.mac: str = kwargs.get(NetworkUtils.MAC_KEY, NetworkUtils.INVALID_MAC)
    
    def _connect(self, **kwargs) -> bool:
        """Connect to the device by url and return True if successful, False otherwise."""
        self.session = requests.Session()
        self.session.headers = self.headers
        
         # Disable SSL certificate verification
        self.session.verify = False

        # make a request to the first production endpoint to check if the device is reachable
        response = self.session.get(self.ip + self.ENDPOINTS[Enphase.PRODUCTION])
        
        if response.status_code != 200:
            logger.error(f"Failed to connect to {self.ip}. Reason: {response.text}")
            return False
        
        self.mac = NetworkUtils.get_mac_from_ip(self.ip)
        
        return self.mac != NetworkUtils.INVALID_MAC

    def _disconnect(self) -> None:
        self.session.close()
        self._is_disconnected = True
    
    def _read_harvest_data(self, force_verbose: bool = False) -> dict:
        data: dict = {}
        # Read data from all endpoints and return the result
        for endpoint_name, endpoint_path in self.ENDPOINTS.items():
            response = self.session.get(self.ip + endpoint_path)
            # logger.info(f"Response: {response.json()}")
            if response.status_code != 200:
                logger.error(f"Failed to read data from endpoint {endpoint_name}")
                continue
            data[endpoint_name] = response.json()
        return data
       
    def is_open(self) -> bool:
        return self.session and self.session.get(self.ip + self.ENDPOINTS[Enphase.PRODUCTION]).status_code == 200
    
    def get_backoff_time_ms(self, harvest_time_ms: int, previous_backoff_time_ms: int) -> int:
        return 1000*60*10 # 10 minutes
    
    def get_harvest_data_type(self) -> HarvestDataType:
        return HarvestDataType.REST_API
    
    def get_config(self) -> dict:
        return {
            ICom.CONNECTION_KEY: Enphase.CONNECTION,
            self.ip_key(): self.ip,
            self.mac_key(): self.mac, 
            self.bearer_token_key(): self.bearer_token
        }
    
    def get_name(self) -> str:
        return self.CONNECTION.lower()
    
    def clone(self) -> 'ICom':
        return Enphase(**self.get_config())
    

    def _clone_with_host(self, host: HostInfo) -> Optional[ICom]:

        if host.mac != self.mac:
            return None
        
        config = self.get_config()
        config[self.ip_key()] = host.ip
        config[self.port_key()] = host.port
        return Enphase(**config)
    
    def _scan_for_devices(self, domain: str) -> Optional['Enphase']:
        mdns_services: List[mdns.ServiceResult] = mdns.scan(5, domain)
        for service in mdns_services:
            if service.address and service.port:
                enphase = Enphase(service.address, service.port, self.bearer_token)
                if enphase.connect():
                    return enphase
        return None
    
    def find_device(self) -> 'ICom':
        """ If there is an id we try to find a device with that id, using multicast dns for for supported devices"""
        if self.mac != NetworkUtils.INVALID_MAC:
            # TODO: This is unknown at this point
            domain_names = {"_enphase-envoy._tcp.local.":{"name": "Enphase IQ Gateway"}}

            for domain, info in domain_names.items():
                enphase = self._scan_for_devices(domain)
                if enphase:
                    enphase.model_name = info["name"]
                    return enphase
        return None
            
    def get_SN(self) -> str:
        return self.mac
        
        
        
    