from abc import ABC, abstractmethod
from .supported_inverters.profiles import InverterProfile
from enum import Enum
from server.network.network_utils import NetworkUtils

class HarvestDataType(Enum):
    MODBUS_REGISTERS = "modbus_registers"
    SUNSPEC = "sunspec_json"
    P1_TELNET = "p1_telnet_json"
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
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def is_terminated(self) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def reconnect(self) -> bool:
        pass
    
    @abstractmethod
    def is_open(self) -> bool:
        pass
    
    @abstractmethod
    def read_harvest_data(self, force_verbose) -> dict:
        pass
    
    @abstractmethod
    def get_harvest_data_type(self) -> str:
        pass
    
    @abstractmethod
    def get_config(self) -> dict:
        pass
    
    @abstractmethod
    def get_profile(self) -> InverterProfile:
        pass
    
    @abstractmethod
    def clone(self, ip: str) -> 'ICom':
        pass
    
    @abstractmethod
    def find_device(self) -> 'ICom':
        pass
    
    @abstractmethod
    def get_SN(self) -> str:
        pass
