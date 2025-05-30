import json
import logging
from server.network.wifi import get_connection_configs, is_connected, get_ip_address, get_ip_addresses_with_interfaces
from server.network import macAddr
from ..handler import GetHandler
from ..requestData import RequestData


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
            returns={self.IP: "string, containing the IP local network address of the device. 0.0.0.0 is returned if no network is available.",
                     self.PORT: "int, containing the port of the REST server.",
                     self.ETH0_MAC: f"string, the mac adress of the first ethernet adapter or {self.NA} if not available",
                     self.WLAN0_MAC: f"string, the mac adress of the first wifi adapter or {self.NA} if not available",
                     self.INTERFACES: f"dictionary, interface and ip adress pairs, typically starts with en - for ethernet or wl for wifi (wlan)",
                    }
        )

    def get(self, port: int) -> dict:
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
            self.PORT: port,
            self.ETH0_MAC: eth0,
            self.WLAN0_MAC: wlan0,
            self.INTERFACES : {iface: ip for iface, ip in ip_interfaces}
        }
        return response


    def do_get(self, data: RequestData):

        return 200, json.dumps(self.get(data.bb.rest_server_port))
