from abc import ABC, abstractmethod
from .supported_inverters.profiles import InverterProfile
# Enum for the type of harvest data

class HarvestDataType:
    MODBUS_REGISTERS = "modbus_registers"
    JSON_DATA = "json_data"
    UNDEFINED = "undefined"

class ICom(ABC):
    
    # HarvestDataType Enum
    data_type = HarvestDataType.UNDEFINED

    @abstractmethod
    def connect(self) -> bool:
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