from zeroconf import Zeroconf, ServiceInfo
import socket
from typing import List, Any, Dict


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
