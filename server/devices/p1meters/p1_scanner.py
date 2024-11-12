'''
This module contains the logic to scan the network for P1 meters
'''


from typing import Callable, Dict, List, Optional
from server.devices.ICom import ICom
from server.devices.p1meters import p1_factory
from server.network import mdns
from server.network.network_utils import HostInfo, NetworkUtils
import logging

logger = logging.getLogger(__name__)

def scan_for_p1_device(meter_serial_number:str) -> Optional[ICom]:
    '''
    Scan for a P1 meter, returns the first P1 meter that matches the serial number
    '''
    p1 = _scan_for_rest_device(meter_serial_number)
    if p1:
        return p1
    p1 = _scan_for_telnet_device(meter_serial_number)
    if p1:
        return p1

    return None

def _scan_for_device(meter_serial_number:str, domain_names:Dict[str,dict], ports:List[int], factory_method:Callable[[str, HostInfo], Optional[ICom]]) -> Optional[ICom]:
    for domain, info in domain_names.items():
        hosts = _mdns_scan_for_devices(domain)
        for host in hosts:
            p1 = factory_method(meter_serial_number, host)
            if p1:
                return p1
            
    # lets scan the network for devices
    hosts = NetworkUtils.get_hosts(ports, 5)
    for host in hosts:
        p1 = factory_method(meter_serial_number, host)
        if p1:
            return p1
    return None

def _scan_for_telnet_device(meter_serial_number:str) -> Optional[ICom]:
    '''
    Scan for a Telnet based P1 meter, returns the first P1 meter that matches the serial number
    '''

    if meter_serial_number:
        domain_names = {"_currently._tcp.local.":{"name": "currently_one"},
                        #  "_hwenergy._tcp.local.":{"name": "home_wizard_p1"},
                        }
        return _scan_for_device(meter_serial_number, domain_names, [23], p1_factory.create_telnet_device)
    
    return None

def _mdns_scan_for_devices(domain: str) -> List[HostInfo]:
        mdns_services: List[mdns.ServiceResult] = mdns.scan(5, domain)
        hosts = []
        for service in mdns_services:
            if service.address and service.port:
                hosts.append(HostInfo(service.address, service.port, NetworkUtils.INVALID_MAC))
                
        return hosts

def _scan_for_rest_device(meter_serial_number:str) -> Optional[ICom]:
    '''
    Scan for a REST based P1 meter
    '''
    
    if meter_serial_number:
        # TODO: This is unknown at this point
        domain_names = {"_jemacp1._tcp.local.":{"name": "currently_one"},
                        #  "_hwenergy._tcp.local.":{"name": "home_wizard_p1"},
                        }
        return _scan_for_device(meter_serial_number, domain_names, [80], p1_factory.create_rest_device) 
            
    # notthing to connect to
    return None



