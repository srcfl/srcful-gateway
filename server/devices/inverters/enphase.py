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
    Enphase device class fetching data from Enphase IQ Gateway using the local REST API.
    A token is required to access the REST API. The token can be provided either directly or using the username/password and IQ Gateway serial number. If the token is provided the username/password and IQ Gateway serial number are ignored.
    The token is automatically fetched when the device is connected (it there is no token)
    """

    CONNECTION = "ENPHASE"
    
    # Endpoint names
    PRODUCTION = "production"
    
    # Endpoint paths
    ENDPOINTS = {
        PRODUCTION: "/production.json"
    }
    
    model_name: str
    
    @staticmethod
    def bearer_token_key():
        return "bearer_token"

    @staticmethod
    def username_key():
        return "username"
    
    @staticmethod
    def password_key():
        return "password"
    
    @staticmethod
    def iq_gw_serial_key():
        return "iq_gw_serial"
    
    @staticmethod
    def get_supported_devices():
        return {Enphase.CONNECTION: {'device_type': 'enphase', 'display_name': 'Enphase', 'protocol': 'http'}}
    
    @staticmethod
    def get_config_schema():
        return {
            **TCPDevice.get_config_schema(Enphase.CONNECTION),
            Enphase.bearer_token_key(): 'string, (optional) Bearer token for the device, either the token is provided or the username/password and iq gateway serial number.',
            Enphase.username_key(): 'string, (optional) Username for the device',
            Enphase.password_key(): 'string, (optional) Password for the device',
            Enphase.iq_gw_serial_key(): 'string, (optional) IQ Gateway serial number'
        }
    
    def make_get_request(self, path: str) -> requests.Response:
        return self.session.get(self.base_url + path)

    def __init__(self, **kwargs) -> None:

        self.username: str = kwargs.get(self.username_key(), "")
        self.password: str = kwargs.get(self.password_key(), "")
        self.iq_gw_serial: str = kwargs.get(self.iq_gw_serial_key(), "")

        self.bearer_token: str = kwargs.get(self.bearer_token_key(), "")

        if self.bearer_token == "":
            if not self.username or not self.password or not self.iq_gw_serial:
                raise ValueError("Bearer token or username/password is required")
        
        ip: str = kwargs.get(self.IP, None)
        TCPDevice.__init__(self, ip, kwargs.get(self.PORT, 80))
        
        self.base_url = f"http://{self.ip}:{self.port}"
        
        self.session: requests.Session = None
        self.mac: str = kwargs.get(NetworkUtils.MAC_KEY, NetworkUtils.INVALID_MAC)
    
    def _connect(self, **kwargs) -> bool:
        """Connect to the device by url and return True if successful, False otherwise."""

        if not self.bearer_token:
            self.bearer_token = self._get_bearer_token(self.iq_gw_serial, self.username, self.password)
            
            # If the bearer token is still empty, there is no point in continuing
            if not self.bearer_token:
                return False
        
        self.session = requests.Session()
        
        # Disable SSL certificate verification
        self.session.verify = False
        
        # Update headers with current bearer token
        self.session.headers = {"Authorization": f"Bearer {self.bearer_token}"}

        # make a request to the first production endpoint to check if the device is reachable
        response = self.make_get_request(self.ENDPOINTS[Enphase.PRODUCTION])
        
        if response.status_code != 200:
            logger.error(f"Failed to connect to {self.ip}. Reason: {response.text}")
            return False
        
        self.mac = NetworkUtils.get_mac_from_ip(self.ip)
        
        return self.mac != NetworkUtils.INVALID_MAC
    
    def _get_bearer_token(self, serial: str, username: str, password: str) -> str:
        envoy_serial=serial
        data = {'user[email]': username, 'user[password]': password}
        response = requests.post('http://enlighten.enphaseenergy.com/login/login.json?', data=data, timeout=10) 
        response_data = response.json()
        data = {'session_id': response_data['session_id'], 'serial_num': envoy_serial, 'username': username}
        response = requests.post('http://entrez.enphaseenergy.com/tokens', json=data, timeout=10)
        token_raw = response.text

        return token_raw

    def _disconnect(self) -> None:
        self.session.close()
        self._is_disconnected = True
    
    def _read_harvest_data(self, force_verbose: bool = False) -> dict:
        data: dict = {}
        # Read data from all endpoints and return the result
        for endpoint_name, endpoint_path in self.ENDPOINTS.items():
            response = self.make_get_request(endpoint_path)
            # logger.info(f"Response: {response.json()}")
            if response.status_code != 200:
                logger.error(f"Failed to read data from endpoint {endpoint_name}")
                continue
            data[endpoint_name] = response.json()
        return data
       
    def is_open(self) -> bool:
        try:
            return self.session and self.make_get_request(self.ENDPOINTS[Enphase.PRODUCTION]).status_code == 200 and not self.is_disconnected()
        except Exception as e:
            logger.warning("Error checking device status: %s", str(e))
            return False
    
    def get_backoff_time_ms(self, harvest_time_ms: int, previous_backoff_time_ms: int) -> int:
        return 1000*30 # 30 seconds
    
    def get_harvest_data_type(self) -> HarvestDataType:
        return HarvestDataType.REST_API
    
    def get_config(self) -> dict:
        return {
            **super().get_config(),
            self.mac_key(): self.mac, 
            self.bearer_token_key(): self.bearer_token
        }
    
    def _get_connection_type(self) -> str:
        return Enphase.CONNECTION
    
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
                enphase = Enphase(ip=service.address, port=service.port, bearer_token=self.bearer_token)
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
        
        
        
    