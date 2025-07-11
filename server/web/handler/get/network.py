import json
import logging
from server.network.network_utils import NetworkUtils
from ..handler import GetHandler
from ..requestData import RequestData


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AddressHandler(GetHandler):

    @property
    def IP(self):
        return "ip"

    @property
    def ETH0_MAC(self):
        return "eth0_mac"

    @property
    def WLAN0_MAC(self):
        return "wlan0_mac"

    @property
    def INTERFACES(self):
        return "interfaces"

    @property
    def WIFI_CONNECTED(self):
        return "wifi_connected"

    @property
    def ETHERNET_CONNECTED(self):
        return "ethernet_connected"

    @property
    def INTERNET_CONNECTION(self):
        return "internet_connection"

    @property
    def WIFI_INTERFACE(self):
        return "wifi_interface"

    @property
    def WIFI_SSID(self):
        return "wifi_ssid"

    @property
    def ETH_INTERFACE(self):
        return "eth_interface"

    @property
    def ETH_CONNECTION(self):
        return "eth_connection"

    @property
    def STATE(self):
        return "state"

    @property
    def CONNECTION_TYPES(self):
        return "connection_types"

    @property
    def NA(self):
        return "n/a"

    def schema(self):
        return self.create_schema(
            "Returns the comprehensive network status of the device",
            returns={
                self.IP: "string, containing the IP local network address of the device. 'no network' is returned if no network is available.",
                self.ETH0_MAC: f"string, the mac address of the first ethernet adapter or {self.NA} if not available",
                self.WLAN0_MAC: f"string, the mac address of the first wifi adapter or {self.NA} if not available",
                self.INTERFACES: "dictionary, interface and ip address pairs, typically starts with en - for ethernet or wl for wifi (wlan)",
                self.WIFI_CONNECTED: "boolean, true if WiFi is connected, false otherwise",
                self.ETHERNET_CONNECTED: "boolean, true if ethernet is connected, false otherwise",
                self.INTERNET_CONNECTION: "boolean, true if internet access is available, false otherwise",
                self.WIFI_SSID: "string, the SSID of the connected WiFi network when WiFi is connected",
            }
        )

    def do_get(self, data: RequestData):

        try:
            ip = NetworkUtils.get_ip_address()
            interfaces = NetworkUtils.get_network_interfaces()
            devices = NetworkUtils.get_network_devices()
            has_internet_access = NetworkUtils.has_internet_access()
            eth0_mac = NetworkUtils.get_eth0_mac()
            wlan0_mac = NetworkUtils.get_wlan0_mac()
            wifi_ssid = NetworkUtils.get_connected_wifi_ssid()

            # Check explicit connection status
            wifi_connected = devices['wifi'] is not None
            ethernet_connected = devices['ethernet'] is not None

            status = {
                'ip': ip,
                'eth0_mac': eth0_mac,
                'wlan0_mac': wlan0_mac,
                'interfaces': interfaces,
                'wifi_connected': wifi_connected,
                'ethernet_connected': ethernet_connected,
                'internet_connection': has_internet_access,
                'wifi_ssid': wifi_ssid,

            }
            return 200, json.dumps(status)
        except Exception as e:
            return {'error': str(e)}
