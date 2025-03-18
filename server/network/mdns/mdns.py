import time
from typing import List, Dict, Any, Optional, Union
import logging
from zeroconf import ServiceBrowser, Zeroconf, ServiceListener, ServiceInfo
from threading import Lock


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_scan_lock = Lock()
_is_scanning = False


def is_scanning() -> bool:
    global _is_scanning
    return _is_scanning


class ServiceResult:
    def __init__(self, name: str, address: Optional[str], port: Optional[int], properties: Dict[bytes, Any]):
        self.name = name
        self.address = address
        self.port = port
        self.properties = {k.decode(): v.decode() if isinstance(v, bytes) else v for k, v in properties.items()}

    def __str__(self):
        return f"{self.name} ({self.address}:{self.port})"

    def __repr__(self):
        return f"MDNSServiceResult(name='{self.name}', address='{self.address}', port={self.port}, properties={self.properties})"


class _Listener(ServiceListener):
    def __init__(self) -> None:
        self.services: Dict[str, ServiceResult] = {}

    def remove_service(self, zeroconf: Zeroconf, type: str, name: str) -> None:
        if name in self.services:
            del self.services[name]

    def add_service(self, zeroconf: Zeroconf, type: str, name: str) -> None:
        info: Optional[ServiceInfo] = zeroconf.get_service_info(type, name)
        if info:
            self.services[name] = ServiceResult(
                name=name,
                address=info.parsed_addresses()[0] if info.parsed_addresses() else None,
                port=info.port,
                properties=info.properties
            )


def scan(duration: int = 5, services: Union[str, List[str]] = ["_http._tcp.local."]) -> List[ServiceResult]:
    """Scan for mDNS services of the specified type(s).

    Args:
        duration: The duration in seconds to scan for services
        services: A service type string (e.g. "_http._tcp.local.") or list of service types

    Returns:
        A list of discovered services
    """
    global _is_scanning

    if not _scan_lock.acquire(blocking=False):
        logger.warning("An mDNS scan is already in progress. Skipping this request.")
        return []

    try:
        _is_scanning = True
        zeroconf = Zeroconf()
        listener = _Listener()

        # Convert string to list if a single service is provided as a string
        if isinstance(services, str):
            services_list = [services]
        else:
            services_list = services

        browser = ServiceBrowser(zeroconf, services_list, listener)
        time.sleep(duration)
        browser.cancel()
        zeroconf.close()
        return list(listener.services.values())
    finally:
        _is_scanning = False
        _scan_lock.release()


def scan_for_compatible_devices() -> List[ServiceResult]:
    services = ["_enphase-envoy._tcp.local.",
                "_jemacp1._tcp.local.",
                "_hwenergy._tcp._tcp.local.",
                "_currently._tcp.local."]

    return scan(services=services)
