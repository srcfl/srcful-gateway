import sunspec2.modbus.client as client
from typing_extensions import TypeAlias
from .ICom import ICom
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ModbusSunspec(ICom):
    """
    ModbusSunspec class
    """
    
    
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
        return self.client.is_connected()
    
    def read_harvest_data(self, force_verbose=False) -> dict:
        try:
            self.inverter.read()
            
            if force_verbose:
                payload_verbose = self.client.get_dict(True)
                return payload_verbose
            else:
                payload_verbose = self.inverter.get_dict(True)

                payload = {}
                payload["Hz"] = payload_verbose["Hz"]
                payload["W"] = payload_verbose["W"]
                payload["DCW"] = payload_verbose["DCW"]
                
                return payload
        except Exception as e:
            logger.error("Error reading harvest data: %s", e)
            return {}
    
    def get_harvest_data_type(self) -> str:
        return self.data_type
    
    def get_config(self):
        return {
            "mode": "SUNSPEC",
            "host": self.host,
            "port": self.port,
            "slave_id": self.slave_id
        }
        
    def get_profile(self):
        pass