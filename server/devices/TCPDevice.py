from typing import Optional
from server.devices.Device import Device
from server.devices.ICom import ICom
from server.network.network_utils import NetworkUtils, HostInfo
from server.e_system.types import EBaseType
from typing import List

from abc import ABC, abstractmethod


class TCPDevice(Device, ABC):
    ''' Base class for devices that connect via TCP/IP '''

    PROTOCOL = "protocol"

    @property
    def IP(self) -> str:
        return self.ip_key()

    @staticmethod
    def ip_key() -> str:
        return "ip"

    @property
    def MAC(self) -> str:
        return self.mac_key()

    @staticmethod
    def mac_key() -> str:
        return "mac"

    @property
    def PORT(self) -> str:
        return self.port_key()

    @staticmethod
    def port_key() -> str:
        return "port"

    def __init__(self, ip: str, port: int) -> None:
        super().__init__()

        self.ip = ip
        self.port = port

    @staticmethod
    def get_config_schema(connection: str):
        return {
            **Device.get_config_schema(connection),
            TCPDevice.ip_key(): "string - IP address or hostname of the device",
            TCPDevice.port_key(): "int - port of the device",
        }

    def get_config(self) -> dict:
        return {
            **Device.get_config(self),
            self.IP: self.ip,
            self.PORT: self.port,
        }

    def compare_host(self, other: ICom) -> bool:
        # check if other is also a TCPDevice and has the same IP and PORT
        if isinstance(other, TCPDevice):
            return self.ip == other.ip and self.port == other.port
        return False

    def find_device(self) -> Optional['ICom']:
        port = self.get_config()[self.PORT]  # get the port from the previous device config
        hosts = NetworkUtils.get_hosts([int(port)], NetworkUtils.DEFAULT_TIMEOUT)

        if len(hosts) > 0:
            for host in hosts:
                clone = self._clone_with_host(host)
                if clone is not None:
                    return clone
        return None

    @abstractmethod
    def _clone_with_host(self, host: HostInfo) -> Optional[ICom]:
        pass

    def get_esystem_data(self) -> List[EBaseType]:
        return []
