from zeroconf import ServiceBrowser, Zeroconf, ServiceListener, ServiceInfo
import time
import socket
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
    """Scan for mDNS services of the specified type."""
    zeroconf = Zeroconf()
    listener = _Listener()
    browser = ServiceBrowser(zeroconf, service_type, listener)
    time.sleep(duration)
    browser.cancel()
    zeroconf.close()
    return list(listener.services.values())


class MDNSAdvertiser:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self._services: List[ServiceInfo] = []

    def get_ip_address(self) -> str:
        """Get the local IP address of the host."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except Exception:
            return "127.0.0.1"

    def register_gateway(self, hostname: str = "sourceful", port: int = 80, properties: Dict[str, Any] = None) -> None:
        """Register the gateway as an mDNS service."""
        if properties is None:
            properties = {}

        ip_address = self.get_ip_address()
        service_info = ServiceInfo(
            "_sourceful._tcp.local.",
            f"{hostname}._sourceful._tcp.local.",
            addresses=[socket.inet_aton(ip_address)],
            port=port,
            properties=properties,
            server=f"{hostname}.local."
        )

        self.zeroconf.register_service(service_info)
        self._services.append(service_info)

    def unregister(self) -> None:
        """Unregister all services and close the Zeroconf instance."""
        for service in self._services:
            self.zeroconf.unregister_service(service)
        self._services.clear()
        self.zeroconf.close()
