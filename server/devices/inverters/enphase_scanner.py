"""
This module contains the logic to scan the network for Enphase devices
"""

from dataclasses import dataclass
from server.devices.inverters.enphase import Enphase
from server.network.network_utils import HostInfo, NetworkUtils
from server.network import mdns
from typing import List, Optional, Dict, Callable
from server.devices.ICom import ICom


def scan_for_enphase_devices() -> List[ICom]:
    """
    Scan for all Enphase devices on the network
    """
    devices:List[ICom] = []
    for scan_info in _get_scan_info():
        devices.extend(scan_info.scan_for_devices())
    return devices

def scan_for_enphase_device(mac:str) -> Optional[ICom]:
    """
    Scan for an Enphase device with the given MAC address
    """
    for scan_info in _get_scan_info():
        enphase = scan_info.scan_for_device(mac)
        if enphase:
            return enphase
    return None



@dataclass
class _ScanInfo:
    domain_names: Dict[str,dict]
    ports: List[int]
    factory_method_msn: Callable[[Optional[str], HostInfo], Optional[ICom]]
    
    def scan_for_device(self, mac:str) -> Optional[ICom]:
        """
        Scan for an Enphase device with the given MAC address
        """
        devices = self._scan_for_devices(mac, return_first=True)
        if devices:
            return devices[0]
        return None


    def scan_for_devices(self) -> List[ICom]:
        """
        Scan for all Enphase devices on the network
        """
        return self._scan_for_devices(None, return_first=False)
    
    def _scan_for_devices(self, mac:Optional[str], return_first:bool=False) -> List[ICom]:
        devices:List[ICom] = []
        for domain, info in self.domain_names.items():
            
            hosts:List[HostInfo] = _mdns_scan_for_devices(domain)
            for host in hosts:
                enphase = self.factory_method_msn(mac, host)
                if enphase:
                    devices.append(enphase)
                    if return_first:
                        return devices
        
        # lets scan the network for devices
        hosts = NetworkUtils.get_hosts(self.ports, 5)
        for host in hosts:
            enphase = self.factory_method_msn(mac, host)
            if enphase:
                devices.append(enphase)
                if return_first:
                    return devices
        return devices
    

def _get_scan_info() -> _ScanInfo:
    domain_names = {"_enphase-envoy._tcp.local.":{"name": "Enphase IQ Gateway"}}
    ports = [80]
    return _ScanInfo(domain_names, ports, Enphase.create_from_msn)


def _mdns_scan_for_devices(domain:str) -> List[HostInfo]:
    mdns_services: List[mdns.ServiceResult] = mdns.scan(5, domain)
    return [HostInfo(ip=service.address, port=service.port) for service in mdns_services if service.address and service.port]



