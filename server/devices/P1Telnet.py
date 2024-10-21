import logging
import telnetlib
from typing import Callable, List
from pymodbus.exceptions import ConnectionException, ModbusException, ModbusIOException

from server.network import mdns as mdns
from .supported_inverters.profiles import InverterProfiles, InverterProfile
from .ICom import HarvestDataType, ICom
from server.network.network_utils import NetworkUtils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class P1Telnet(ICom):
    """
    P1Telnet class
    """
    client: telnetlib.Telnet
    ip: str
    port: int
    id: str

    def __init__(self, ip: str, port: int = 23, id: str = ""):
        self.ip = ip
        self.port = port
        self.id = id

    def connect(self) -> bool:
        return self._connect(telnetlib.Telnet)
        
    
    def _connect(self, telnet_factory: Callable[[str, int, int], telnetlib.Telnet]) -> bool:
        try:
            self.client = telnet_factory(self.ip, self.port, 5)
            logger.info(f"Successfully connected to {self.ip}:{self.port}")
            harvest = self.read_harvest_data(False)
            if self.id == "":
                self.id = harvest['serial_number']
                return True
            else:
                return self.id == harvest['serial_number']

        except Exception as e:
            logger.error(f"Failed to connect to {self.ip}:{self.port}: {str(e)}")
            return False
        
    
    def is_valid(self) -> bool:
        return self.id != ""
    
    def disconnect(self) -> None:
        if self.client:
            self.client.close()
    
    def reconnect(self) -> bool:
        self.disconnect()
        return self.connect()
    
    def is_open(self) -> bool:
        return self.client.get_socket() != None
    
    def read_harvest_data(self, force_verbose) -> dict:
        try:
            p1_message = self._read_harvest_data(self.client)

            # Parse the P1 message
            data = self._parse_p1_message(p1_message)
            
            return data
        except Exception as e:
            logger.error(f"Error reading P1 data: {str(e)}")
            raise
        
    def _read_harvest_data(self, telnet_client: telnetlib.Telnet) -> str:
        # Read until the start of a P1 message
        telnet_client.read_until(b"/", timeout=17)
        
        # Read the entire P1 message including the last crc check
        p1_message = "/" + telnet_client.read_until(b"!", timeout=17).decode('ascii') + telnet_client.read_until(b"\r\n", timeout=17).decode('ascii')

        if len(p1_message) < 5:
            logger.error(f"P1 message is too short: {p1_message}")
            raise Exception(f"P1 message is too short: {p1_message}")
        
        return p1_message
            

    def _parse_p1_message(self, message: str) -> dict:
        lines = message.strip().split()
        data = {
            'serial_number': '',
            'rows': []
        }
        
        # Extract serial number from the first line remove the leading '/'
        data['serial_number'] = lines[0][1:]
        
        # Add all other lines to the rows list
        data['rows'] = [line.strip() for line in lines[1:] if line.strip()]
        
        return data


    def get_harvest_data_type(self) -> str:
        return HarvestDataType.P1_TELNET.value
    
    def get_config(self) -> dict:
        return {
            "ip": self.ip,
            "port": self.port,
            "id": self.id
        }
    
    def get_profile(self) -> InverterProfile:
        raise NotImplementedError("get_profile is not implemented for P1Telnet")
    
    def clone(self, ip: str) -> 'ICom':
        return P1Telnet(ip, self.port, self.id)
    
    def find_device(self) -> 'ICom':
        """ If there is an id we try to find a device with that id, using multicast dns for for supported devices"""
        if self.id:
            mdns_services: List[mdns.ServiceResult] = mdns.scan(5, "_currently._tcp.")
            for service in mdns_services:
                if service.address and service.port:
                    p1 = P1Telnet(service.address, service.port, self.id)
                    if p1.connect():
                        return p1
        return None
    
    def get_SN(self) -> str:
        return self.id