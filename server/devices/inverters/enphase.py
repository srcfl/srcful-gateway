from server.devices.TCPDevice import TCPDevice
from ..Device import Device
import logging
import requests
from server.network import mdns as mdns
from ..ICom import HarvestDataType, ICom
from typing import Optional
from server.network.network_utils import HostInfo, NetworkUtils

# Suppress SSL verification warnings (optional)
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

    @staticmethod
    def get_supported_devices():
        return {Enphase.CONNECTION: {'device_type': 'enphase', 'display_name': 'Enphase', 'protocol': 'http'}}
    
    @staticmethod
    def get_config_schema():
        return {
            **TCPDevice.get_config_schema(),
            'bearer_token': 'string, Bearer token for the device'

        }

    def __init__(self, **kwargs):
        
        self.bearer_token: str = kwargs.get("bearer_token", None)
        if not self.bearer_token:
            raise ValueError("Bearer token is required")
        
        self.base_url: str = kwargs.get(self.IP, None)
        self.base_url = NetworkUtils.parse_address(self.base_url)
        
        if not self.base_url:
            raise ValueError("Base URL is required")

        TCPDevice.__init__(self, self.base_url, kwargs.get(self.PORT, 80))
        
        self.headers: dict = {"Authorization": f"Bearer {self.bearer_token}"}
        
        self.session: requests.Session = None
        self.mac: str = NetworkUtils.INVALID_MAC
        
        # Move there to somewhere else more appropriate?
        self.endpoints: dict = {
            "production": "/api/v1/production/inverters",
            "consumption": "/ivp/meters/reports/consumption",
            "energy": "/ivp/pdm/energy"
        }
    
    def _connect(self, **kwargs) -> bool:
        """Connect to the device by url and return True if successful, False otherwise."""
        self.session = requests.Session()
         # Disable SSL certificate verification
        self.session.verify = False

        response = self.session.get(self.base_url, headers=self.headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to connect to {self.base_url}")
            return False
        
        self.mac = NetworkUtils.get_mac_from_ip(self.base_url)
        
        return self.mac != NetworkUtils.INVALID_MAC

    def _disconnect(self) -> None:
        self.session.close()
        self._is_disconnected = True
    
    def _read_harvest_data(self, force_verbose: bool = False) -> dict:
        data: dict = {}
        # Read data from all endpoints and return the result
        for endpoint_name, endpoint_path in self.endpoints.items():
            response = self.session.get(self.base_url + endpoint_path, headers=self.headers)
            # logger.info(f"Response: {response.json()}")
            if response.status_code != 200:
                logger.error(f"Failed to read data from endpoint {endpoint_name}")
                continue
            data[endpoint_name] = response.json()
        return data
       
    def is_open(self) -> bool:
        return self.session and self.session.get(self.base_url, headers=self.headers).status_code == 200
    
    def get_backoff_time_ms(self, harvest_time_ms: int, previous_backoff_time_ms: int) -> int:
        return 1000*60*10 # 10 minutes
    
    def get_harvest_data_type(self) -> HarvestDataType:
        return HarvestDataType.REST_API
    
    def get_config(self) -> dict:
        return {
            ICom.CONNECTION_KEY: Enphase.CONNECTION,
            "base_url": self.base_url,
            "endpoints": self.endpoints,
            "mac": self.mac, 
            "bearer_token": self.bearer_token
        }
    
    def get_name(self) -> str:
        return self.CONNECTION.lower()
    
    def clone(self) -> 'ICom':
        return Enphase(**self.get_config())
    

    def _clone_with_host(self, host: HostInfo) -> Optional[ICom]:

        if host.mac != self.mac:
            return None
        
        config = self.get_config()
        config[self.IP] = host.ip
        return Enphase(**config)
            
    def get_SN(self) -> str:
        return self.mac
        
        
        
    