import sunspec2.modbus.client as client
from sunspec2.modbus.client import SunSpecModbusClientError
from typing_extensions import TypeAlias
from .ICom import ICom, HarvestDataType
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)




class ModbusSunspec(ICom):
    """
    ModbusSunspec class
    """

    CONNECTION = "SUNSPEC"

    @staticmethod
    def list_to_tuple(config: list) -> tuple:
        assert config[ICom.CONNECTION_IX] == ModbusSunspec.CONNECTION, "Invalid connection type"
        ip = config[1]
        port = int(config[2])
        slave_id = int(config[3])
        return (config[ICom.CONNECTION_IX], ip, port, slave_id)
    
    @staticmethod
    def dict_to_tuple(config: dict) -> tuple:
        assert config[ICom.CONNECTION_KEY] == ModbusSunspec.CONNECTION, "Invalid connection type"
        ip = config["host"]
        port = int(config["port"])
        slave_id = int(config["address"])
        return (config[ICom.CONNECTION_KEY], ip, port, slave_id)
    
    # Address, Serial, Port, type, Slave_ID, verbose 
    Setup: TypeAlias = tuple[str | bytes | bytearray, int, int]
    
    def __init__(self, setup: Setup) -> None:
        """
        Constructor
        """
        self.host = setup[0]
        self.port = setup[1]
        self.slave_id = setup[2]
        self.client = None
        self.common = None
        self.inveter = None
        self.data_type = HarvestDataType.SUNSPEC.value
        
    def connect(self) -> bool:
        self.client = client.SunSpecModbusClientDeviceTCP(slave_id=self.slave_id, ipaddr=self.host, ipport=self.port)
        self.client.scan()
        self.client.connect()
        
        logger.info("Models: %s", self.client.models)
        
        if 'inverter' in self.client.models:
            self.inverter = self.client.inverter[0]
            
        return len(self.client.models) > 0
        
    def disconnect(self) -> None:
        self.client.disconnect()
        self._isTerminated = True
    
    def reconnect(self) -> None:
        self.disconnect() and self.connect()
        
    def is_open(self) -> bool:
        return bool(self.client.is_connected())
    
    def read_harvest_data(self, force_verbose=False) -> dict:
        try:
            self.inverter.read()
            
            if force_verbose:
                payload_verbose = self.client.get_dict()
                return payload_verbose
            else:
                payload_verbose = self.inverter.get_dict()
                payload = {}
                payload["Hz"] = payload_verbose["Hz"]
                payload["Hz_SF"] = payload_verbose["Hz_SF"]
                payload["W"] = payload_verbose["W"]
                payload["W_SF"] = payload_verbose["W_SF"]
                payload["DCW"] = payload_verbose["DCW"]
                payload["DCW_SF"] = payload_verbose["DCW_SF"]
                
                return payload
        except Exception as e:
            logger.error("Error reading harvest data: %s", e)
            raise SunSpecModbusClientError(e)
    
    def get_harvest_data_type(self) -> str:
        return self.data_type
    
    def get_config(self):
        return {
            ICom.CONNECTION_KEY: ModbusSunspec.CONNECTION,
            "host": self.host,
            "port": self.port,
            "address": self.slave_id
        }
        
    def get_profile(self):
        pass
    
    def clone(self, host: str) -> 'ModbusSunspec':
        return ModbusSunspec((host, self.port, self.slave_id))