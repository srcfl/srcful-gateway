'''
This module contains the logic to scan the network for P1 meters
'''


from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
from server.devices.ICom import ICom
from server.devices.p1meters import p1_factory
from server.network import mdns
from server.network.network_utils import HostInfo, NetworkUtils
import logging

logger = logging.getLogger(__name__)

def scan_for_p1_devices() -> List[ICom]:
    '''
    Scan for all P1 devices on the network
    '''
    devices:List[ICom] = []
    for scan_info in _get_scan_info():
        devices.extend(scan_info.scan_for_devices())
    return devices


def scan_for_p1_device(meter_serial_number:str) -> Optional[ICom]:
    '''
    Scan for a P1 meter, returns the first P1 meter that matches the serial number
    '''

    if meter_serial_number:
        for scan_info in _get_scan_info():
            p1 = scan_info.scan_for_device(meter_serial_number)
            if p1:
                return p1
    return None



@dataclass
class _ScanInfo:
    domain_names: Dict[str,dict]
    ports: List[int]
    factory_method_msn: Callable[[Optional[str], HostInfo], Optional[ICom]]

    def scan_for_device(self, meter_serial_number:str) -> Optional[ICom]:
        devices = self._scan_for_devices(meter_serial_number, return_first=True)
        if devices:
            return devices[0]
        return None

    def scan_for_devices(self) -> List[ICom]:        
        return self._scan_for_devices(None, return_first=False)
    
    def _scan_for_devices(self, meter_serial_number:Optional[str], return_first:bool=False) -> List[ICom]:
        
        devices:List[ICom] = []

        for domain, info in self.domain_names.items():
            hosts:List[HostInfo] = _mdns_scan_for_devices(domain)
            for host in hosts:
                p1 = self.factory_method_msn(meter_serial_number, host)
                if p1:
                    devices.append(p1)
                    if return_first:
                        return devices
                
        # lets scan the network for devices
        hosts = NetworkUtils.get_hosts(self.ports, 5)
        for host in hosts:
            p1 = self.factory_method_msn(meter_serial_number, host)
            if p1:
                devices.append(p1)
                if return_first:
                    return devices
        return devices

def _get_scan_info() -> List[_ScanInfo]:

    telenet_domain_names = {"_currently._tcp.local.":{"name": "currently_one"}}
    telenet_ports = [23]
    rest_domain_names = {"_jemacp1._tcp.local.":{"name": "jemac_p1_meter"}}
    rest_ports = [80]

    return [
        _ScanInfo(telenet_domain_names, telenet_ports, p1_factory.create_telnet_device_msn),
        _ScanInfo(rest_domain_names, rest_ports, p1_factory.create_rest_device_msn)
    ]

def _mdns_scan_for_devices(domain: str) -> List[HostInfo]:
    return [HostInfo(service.address, service.port, NetworkUtils.get_mac_from_ip(service.address)) for service in mdns.scan(5, domain) if service.address and service.port]
                


