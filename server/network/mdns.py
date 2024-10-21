from zeroconf import ServiceBrowser, Zeroconf, ServiceListener, ServiceInfo
import time
from typing import List, Dict, Any, Optional

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

def scan(duration: int = 5, service_type: str = "_http._tcp.local.") -> List[ServiceResult]:
    zeroconf = Zeroconf()
    listener = _Listener()
    browser = ServiceBrowser(zeroconf, service_type, listener)

    # Scan for the specified duration
    time.sleep(duration)

    zeroconf.close()
    return list(listener.services.values())