from typing import List, Optional

import requests

from server.devices.Device import Device
from server.devices.ICom import HarvestDataType, ICom
from server.devices.p1meters.P1Telnet import P1Telnet
from server.network import mdns

import logging

logger = logging.getLogger(__name__)

class P1Jemac(Device):


    CONNECTION = "P1Jemac"

    
    @staticmethod
    def get_supported_devices():
        return {P1Jemac.CONNECTION: {'device_type': P1Jemac.CONNECTION, 'display_name': 'Jemac P1 Meter'}}
    
    @staticmethod
    def get_config_schema():
        return {
            "ip": "string, IP address or hostname of the device",
            "port": "int, port of the device",
            "meter_serial_number": "optional string, Serial number of the meter",
            "model_name": "optional string, Model name of the meter"
        }


    """
    P1Telnet class
    """
    ip: str
    port: int
    meter_serial_number: str
    model_name: str

    def __init__(self, ip: str, port: int = 23, meter_serial_number: str = "", model_name: str = "jema_p1_meter"):
        self.ip = ip
        self.port = port
        self.meter_serial_number = meter_serial_number
        self.model_name = model_name
        self.endpoint = "/telegram.json"

    def _connect(self, **kwargs) -> bool:
        try:

            harvest = self.read_harvest_data(False)
            if self.meter_serial_number == "":
                self.meter_serial_number = harvest['serial_number']
                return True
            else:
                return self.meter_serial_number == harvest['serial_number']
        except Exception as e:
            logger.error(f"Failed to connect to {self.ip}:{self.port}: {str(e)}")
            return False

    def is_valid(self) -> bool:
        return self.meter_serial_number != ""
    
    def _disconnect(self) -> None:
        pass
       
    def is_open(self) -> bool:
        return True
    
    def _parse_p1_message(self, p1_message: dict) -> dict:
        p1_message = p1_message.get('data', {})
        data =  {
            'serial_number': p1_message[0],
            'rows': p1_message[1:]
        }

        if data['serial_number'] == "":
            raise Exception("Serial number not found")
        
        return data
    
    def _read_harvest_data(self, force_verbose) -> dict:
        try:
            p1_message = requests.get(f"http://{self.ip}:{self.port}{self.endpoint}")
            p1_message.raise_for_status()

            return self._parse_p1_message(p1_message.json())
        except Exception as e:
            logger.error(f"Error reading P1 data: {str(e)}")
            raise
        
    

    def get_harvest_data_type(self) -> str:
        # We return data in the same format as the P1Telnet device
        return HarvestDataType.P1_TELNET.value
    
    def get_config(self) -> dict:
        return {
            ICom.CONNECTION_KEY: P1Telnet.CONNECTION,
            "ip": self.ip,
            "port": self.port,
            "meter_serial_number": self.meter_serial_number
        }
    
    def get_name(self) -> str:
        return "P1Telnet"
    
    def clone(self, ip: Optional[str] = None) -> 'ICom':
        if ip is None:
            ip = self.ip
        return P1Telnet(ip, self.port, self.meter_serial_number)

    def _scan_for_devices(self, domain: str) -> Optional['P1Telnet']:
        mdns_services: List[mdns.ServiceResult] = mdns.scan(5, domain)
        for service in mdns_services:
            if service.address and service.port:
                p1 = P1Telnet(service.address, self.port, self.meter_serial_number)
                if p1.connect():
                    return p1
        return None
    
    def find_device(self) -> 'ICom':
        """ If there is an id we try to find a device with that id, using multicast dns for for supported devices"""
        if self.meter_serial_number:
            # TODO: This is unknown at this point
            domain_names = {"_jemacp1._tcp.local.":{"name": "currently_one"},
                            #  "_hwenergy._tcp.local.":{"name": "home_wizard_p1"},
                           }

            for domain, info in domain_names.items():
                p1 = self._scan_for_devices(domain)
                if p1:
                    p1.model_name = info["name"]
                    return p1
        return None
    
    def get_SN(self) -> str:
        return self.meter_serial_number

    def get_backoff_time_ms(self, harvest_time_ms: int, previous_backoff_time_ms: int) -> int:
        # p1 meters typically send data every 10 seconds
        return 10 * 1000