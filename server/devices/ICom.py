from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum

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


class ICom(ABC):
    
    # HarvestDataType Enum
    data_type = HarvestDataType.UNDEFINED

    CONNECTION_KEY = "connection"
    CONNECTION_IX = 0


    def get_der_types(self) -> list[DER_TYPE]:
        pass
    
    # def __eq__(self, other: 'ICom') -> bool:
    #     return self.get_config()[NetworkUtils.MAC_KEY] == other.get_config()[NetworkUtils.MAC_KEY]

    @abstractmethod
    def connect(self) -> bool:
        ''' Establish a connection to the device using the configuration of the device. If the device has a serial number it will only connect to the device with that serial number. If it has no serial number it will read the serial number from the device.'''
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
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
    def clone(self, ip: Optional[str] = None) -> 'ICom':
        pass
    
    @abstractmethod
    def find_device(self) -> 'ICom':
        pass
    
    @abstractmethod
    def get_SN(self) -> str:
        pass
