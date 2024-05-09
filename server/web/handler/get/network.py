import json
import nmap
import socket
from server.wifi.wifi import get_connection_configs, is_connected, get_ip_address
from ..handler import GetHandler
from ..requestData import RequestData

COMMON_INVERTER_PORTS = [502, 1502, 8877]

class NetworkHandler(GetHandler):
    def schema(self):
        return self.create_schema(
            "Returns the list of networks",
            returns={"connections": "list of dicts, containing the configured networks."}
        )

    def do_get(self, data: RequestData):
        return 200, json.dumps({"connections": get_connection_configs()})


class AddressHandler(GetHandler):
    def schema(self):
        return self.create_schema(
            "Returns the IP address of the device",
            returns={"ip": "string, containing the IP local network address of the device. 127.0.0.1 is returned if no network is available.",
                     "port": "int, containing the port of the REST server."}
        )



    def do_get(self, data: RequestData):
        if is_connected():
            return 200, json.dumps({"ip": get_ip_address(), "port": data.bb.rest_server_port})
        else:
            return 200, json.dumps({"ip": "no network", "port": 0})


# A class to scan for modbus devices on the network
class ModbusScanHandler(GetHandler):
    def schema(self):
        return self.create_schema(
            "Scans the network for modbus devices",
            returns={"devices": "a list of JSON Objects, each containing the host and port of a modbus device."}
        )

    def do_get(self, data: RequestData):

        local_ip = get_ip_address()

        # Extract the network prefix from the local IP address
        network_prefix = '.'.join(local_ip.split('.')[:-1]) + '.0/24'

        # Convert the list of common ports to a comma separated string for nmap
        common_ports = ','.join(map(str, COMMON_INVERTER_PORTS)) 

        nm = nmap.PortScanner()
        nm.scan(network_prefix, ports=common_ports, arguments='-T5')

        modbus_devices = []

        for host in nm.all_hosts():
            for port in COMMON_INVERTER_PORTS:
                if nm[host].has_tcp(port) and nm[host]['tcp'][port]['state'] == 'open':
                    device = {
                    'host': host,
                    'port': port
                    }
                    modbus_devices.append(device)
    
        return 200, json.dumps(modbus_devices)

