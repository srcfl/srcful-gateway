from server.devices.TCPDevice import TCPDevice
import logging
import requests
import xml.etree.ElementTree as ET
from server.devices.inverters.common import INVERTER_CLIENT_NAME
from server.network.mdns import mdns
from server.network.mdns.mdns import ServiceResult
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
    INFORMATION = "information"

    # Endpoint paths
    ENDPOINTS = {
        PRODUCTION: "/production.json",
        INFORMATION: "/info.xml"
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
    def get_supported_devices(verbose: bool = True):
        if verbose:
            return {Enphase.CONNECTION: {
                Enphase.DEVICE_TYPE: 'enphase',
                Enphase.MAKER: 'Enphase',
                Enphase.DISPLAY_NAME: 'Enphase',
                Enphase.PROTOCOL: 'http'
            }}
        else:
            return {Enphase.CONNECTION: {'maker': 'Enphase'}}

    @staticmethod
    def get_config_schema():
        return {
            **TCPDevice.get_config_schema(Enphase.CONNECTION),
            Enphase.bearer_token_key(): 'string, (optional, required if username and password are not provided) Bearer token for the device, either the token is provided or the username/password and iq gateway serial number.',
            Enphase.username_key(): 'string, (optional, required if bearer token is not provided) Username for the device',
            Enphase.password_key(): 'string, (optional, required if bearer token is not provided) Password for the device',
            Enphase.iq_gw_serial_key(): 'string, (optional) IQ Gateway serial number'
        }

    def make_get_request(self, path: str) -> requests.Response:
        return self.session.get(self.base_url + path, timeout=45)

    def __init__(self, **kwargs) -> None:

        logger.info(f"Enphase __init__: kwargs: {kwargs}")

        self.username: str = kwargs.get(self.username_key(), "")
        self.password: str = kwargs.get(self.password_key(), "")
        self.iq_gw_serial: str = kwargs.get(self.iq_gw_serial_key(), None)
        self.bearer_token: str = kwargs.get(self.bearer_token_key(), "")

        ip: str = kwargs.get(self.IP, None)
        TCPDevice.__init__(self, ip, kwargs.get(self.PORT, 80))

        self.base_url = f"http://{self.ip}:{self.port}"

        self.session: requests.Session = None
        self.mac: str = kwargs.get(NetworkUtils.MAC_KEY, NetworkUtils.INVALID_MAC)

    def _read_SN(self) -> Optional[str]:
        """Read device information from the info.xml endpoint.

        Returns:
            Optional[str]: The device serial number if successful, None otherwise
        """
        info_response = self.make_get_request(self.ENDPOINTS[Enphase.INFORMATION])
        if info_response.status_code != 200:
            logger.error(f"Failed to get device info from {self.ip}. Reason: {info_response.text}")
            return None

        try:
            root = ET.fromstring(info_response.text)
            sn = root.find(".//device/sn").text
            logger.info(f"Found device serial number: {sn}")
            return sn
        except (ET.ParseError, AttributeError) as e:
            logger.error(f"Failed to parse device info XML: {str(e)}")
            return None

    def _connect(self, **kwargs) -> bool:
        """Connect to the device by url and return True if successful, False otherwise."""

        if self.bearer_token == "":
            if not self.username or not self.password or not self.iq_gw_serial:
                raise ValueError("Bearer token or username, password, and iq gateway serial number is required")

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

        # Get device info to read serial number
        if self.iq_gw_serial is None:
            self.iq_gw_serial = self._read_SN()

        if not self.iq_gw_serial:
            return False

        # make a request to the production endpoint to check if the device is reachable
        response = self.make_get_request(self.ENDPOINTS[Enphase.PRODUCTION])

        if response.status_code != 200:
            logger.error(f"Failed to connect to {self.ip}. Reason: {response.text}")
            return False

        self.mac = NetworkUtils.get_mac_from_ip(self.ip)

        return self.mac != NetworkUtils.INVALID_MAC

    def _get_bearer_token(self, serial: str, username: str, password: str) -> str:
        envoy_serial = serial
        data = {'user[email]': username, 'user[password]': password}
        try:
            response = requests.post('https://enlighten.enphaseenergy.com/login/login.json?', data=data, timeout=10)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            response_data = response.json()

            if 'session_id' not in response_data:
                logger.error("Failed to get session_id from Enphase login response")
                return ""

            data = {'session_id': response_data['session_id'], 'serial_num': envoy_serial, 'username': username}
            response = requests.post('https://entrez.enphaseenergy.com/tokens', json=data, timeout=10)
            response.raise_for_status()
            token_raw = response.text

            if not token_raw:
                logger.error("Received empty token from Enphase API")
                return ""

            return token_raw

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get bearer token from Enphase: {str(e)}")
            return ""
        except ValueError as e:
            logger.error(f"Failed to parse Enphase response: {str(e)}")
            return ""

    def _disconnect(self) -> None:
        self.session.close()
        self._is_disconnected = True

    def _read_harvest_data(self, force_verbose: bool = False) -> dict:
        data: dict = {}
        # Read data from the production endpoint
        response = self.make_get_request(self.ENDPOINTS[Enphase.PRODUCTION])
        if response.status_code != 200:
            logger.error(f"Failed to read data from {self.ip}. Reason: {response.text}")
            return {}

        data[Enphase.PRODUCTION] = response.json()
        return data

    def _is_open(self) -> bool:
        try:
            return self.session and self.make_get_request(self.ENDPOINTS[Enphase.PRODUCTION]).status_code == 200
        except Exception as e:
            logger.warning("Error checking device status: %s", str(e))
            return False

    def get_backoff_time_ms(self, harvest_time_ms: int, previous_backoff_time_ms: int) -> int:
        return 1000*30  # 30 seconds

    def get_harvest_data_type(self) -> HarvestDataType:
        return HarvestDataType.REST_API

    def get_config(self) -> dict:
        return {
            **super().get_config(),
            self.iq_gw_serial_key(): self.iq_gw_serial,
            self.mac_key(): self.mac,
            self.bearer_token_key(): self.bearer_token
        }

    def _get_connection_type(self) -> str:
        return Enphase.CONNECTION

    def get_name(self) -> str:
        return self.CONNECTION.lower()

    def get_client_name(self) -> str:
        return INVERTER_CLIENT_NAME + "." + self.get_name()

    def clone(self) -> 'ICom':
        return Enphase(**self.get_config())

    def _clone_with_host(self, host: HostInfo) -> Optional[ICom]:

        if host.mac != self.mac:
            return None

        config = self.get_config()
        config[self.ip_key()] = host.ip
        config[self.port_key()] = host.port
        return Enphase(**config)

    def find_device(self) -> 'ICom':
        """ If there is an id we try to find a device with that id, using multicast dns for for supported devices"""
        res: ServiceResult = mdns.scan(5, "_enphase-envoy._tcp.local.")
        if len(res) == 0:
            return None
        res: ServiceResult = res[0]
        mac = NetworkUtils.get_mac_from_ip(res.address)
        host: HostInfo = HostInfo(res.address, res.port, mac)

        clone = self._clone_with_host(host)
        if clone is not None:
            return clone

        return None

    def get_SN(self) -> str:
        return self.iq_gw_serial
