import sunspec2.modbus.client as client
from typing_extensions import TypeAlias
from .ICom import ICom

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
        
    def connect(self) -> None:
        self.client = client.SunSpecModbusClientDeviceTCP(slave_id=self.slave_id, ipaddr=self.host, ipport=self.port)
        self.client.scan()
        
    def disconnect(self) -> None:
        self.client.disconnect()
        self._isTerminated = True
    
    def reconnect(self) -> None:
        self.disconnect() and self.connect()
        
    def is_open(self) -> bool:
        return self.client.is_connected()
    
    def read_harvest_data(self, force_verbose=False) -> dict:
        self.client.get_json(True)
    
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