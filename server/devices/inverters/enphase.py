from ..Device import Device
import logging
import requests
from ..supported_devices.profiles import ModbusDeviceProfiles
from server.network import mdns as mdns
from ..ICom import HarvestDataType, ICom
from typing import Optional, List

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Enphase(Device):
    """
    Enphase device class
    
    Attributes:
        base_url (str): The base URL for the REST API
        endpoints (dict): Dictionary of available endpoints
        auth_method (str): Authentication method to use
    """

    CONNECTION = "ENPHASE"

    @staticmethod
    def get_supported_devices():
        return {Enphase.CONNECTION: {'id': 'enphase', 'display_name': 'Enphase'}}
    
    @staticmethod
    def get_config_schema():
        return {
           'ip': 'string, IP address or hostname of the device',
           'endpoints': 'dict, Dictionary of endpoints to read data from',
           'bearer_token': 'string, Bearer token for the device'
        }

    def __init__(self, **kwargs):
        
        self.bearer_token: str = kwargs.get("bearer_token", None)
        if not self.bearer_token:
            raise ValueError("Bearer token is required")
        
        self.base_url: str = kwargs.get("base_url", None)   
        if not self.base_url:
            raise ValueError("Base URL is required")
        
        self.endpoints: dict = kwargs.get("endpoints", {})
        
        self.headers: dict = {"Authorization": f"Bearer {self.bearer_token}"}
        
        self.session: requests.Session = None
        self.mac: str = "00:00:00:00:00:00"
    
    def _connect(self, **kwargs) -> bool:
        """Connect to the device by url and return True if successful, False otherwise."""
        self.session = requests.Session()
        response = self.session.get(self.base_url, headers=self.headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to connect to {self.base_url}")
            return False
        
        # self.mac = NetworkUtils.get_mac_address()
        
        return True

    def _disconnect(self) -> None:
        self.session.close()
        self._is_disconnected = True
    
    def _read_harvest_data(self, force_verbose: bool = False) -> dict:
        data: dict = {}
        # Read data from all endpoints and return the result
        for endpoint in self.endpoints:
            response = self.session.get(self.base_url + endpoint, headers=self.headers)
            if response.status_code != 200:
                logger.error(f"Failed to read data from endpoint {endpoint}")
                continue
            data[endpoint] = response.json()

        return data
    
    def is_valid(self) -> bool:
        return self.mac != "00:00:00:00:00:00"
    
    def is_open(self) -> bool:
        return self.session.get(self.base_url, headers=self.headers).status_code == 200
    
    def get_harvest_data_type(self) -> str:
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
        return self.profile.name
    
    def clone(self, ip: Optional[str] = None) -> 'ICom':
        if ip is None:
            ip = self.base_url
        return Enphase(device_type=self.device_type, bearer_token=self.bearer_token, base_url=ip)
    
    def find_device(self) -> 'ICom':
        raise NotImplementedError("Not implemented")
            
    def get_SN(self) -> str:
        return self.mac
        
        
        
    