from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum
from server.devices.supported_devices.data_models import DERData

class HarvestDataType(Enum):
    MODBUS_REGISTERS = "modbus_registers"
    SUNSPEC = "sunspec_json"
    P1_TELNET = "p1_telnet_json"
    REST_API = "rest_api_json"
    UNDEFINED = "undefined"


class DER_TYPE(Enum):
    PV = "pv"
    BATTERY = "battery"
    UTILITY_METER_P1 = "meter_p1"


class DeviceMode(Enum):
    NONE = "none"
    READ = "read"
    CONTROL = "control"
    SELF_CONSUMPTION = "self_consumption"


class ICom(ABC):

    # HarvestDataType Enum
    data_type = HarvestDataType.UNDEFINED
    
    # Default polling interval - can be overridden by implementations
    DEFAULT_HARVEST_INTERVAL_MS = 950

    CONNECTION_KEY = "connection"
    CONNECTION_IX = 0

    @staticmethod
    def connection_key():
        return "connection"

    @abstractmethod
    def get_device_mode(self) -> DeviceMode:
        pass

    @abstractmethod
    def set_device_mode(self) -> None:
        pass
    
    @abstractmethod
    def set_device_mode(self, mode: DeviceMode) -> None:
        pass

    class ConnectionException(Exception):
        def __init__(self, message: str, device: 'ICom', root_cause: Optional[Exception] = None):
            self.message = message
            self.device = device
            self.root_cause = root_cause
            super().__init__(self.message)

    #@abstractmethod
    #def get_der_types(self) -> list[DER_TYPE]:
    #    pass

    # def __eq__(self, other: 'ICom') -> bool:
    #     return self.get_config()[NetworkUtils.MAC_KEY] == other.get_config()[NetworkUtils.MAC_KEY]

    @abstractmethod
    def connect(self) -> bool:
        ''' Establish a connection to the device using the configuration of the device. If the device has a serial number it will only connect to the device with that serial number. If it has no serial number it will read the serial number from the device.'''
        pass

    @abstractmethod
    def is_disconnected(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        ''' Permanently disconnect the device. This will close the connection and release any resources. You cannot reconnect to the device with the same object. Instead create a new object using. eg clone(). '''
        pass

    @abstractmethod
    def get_backoff_time_ms(self, harvest_time_ms: int, previous_backoff_time_ms: int) -> int:
        pass

    @abstractmethod
    def is_open(self) -> bool:
        ''' Check if the device is open and connected. Should only return True if connect has been called and returned True, and the connection is still open/valid.'''
        pass

    @abstractmethod
    def read_harvest_data(self, force_verbose) -> dict:
        pass

    @abstractmethod
    def get_harvest_data_type(self) -> HarvestDataType:
        pass

    @abstractmethod
    def get_config(self) -> dict:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_client_name(self) -> str:
        pass

    @abstractmethod
    def clone(self) -> 'ICom':
        pass

    @abstractmethod
    def compare_host(self, other: 'ICom') -> bool:
        ''' Compare two devices to see if they connect to the same host and service. This should not require a connection to make the comparison.'''
        pass

    @abstractmethod
    def find_device(self) -> Optional['ICom']:
        pass

    @abstractmethod
    def get_SN(self) -> str:
        pass
    
    @abstractmethod
    def dict_to_ders(self, payload: dict | str) -> DERData:
        pass
