from abc import ABC, abstractmethod

# Enum for the type of harvest data

class HarvestDataType:
    MODBUS_REGISTERS = "modbus_registers"
    JSON_DATA = "json_data"
    UNDEFINED = "undefined"

class ICom(ABC):
    
    # HarvestDataType Enum
    data_type = HarvestDataType.UNDEFINED

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    def reconnect(self):
        pass
    
    @abstractmethod
    def read_harvest_data(self):
        pass
    
    @abstractmethod
    def get_harvest_data_type(self):
        pass