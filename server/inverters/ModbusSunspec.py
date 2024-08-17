from ICom import ICom
import sunspec2.modbus.client as client
from typing_extensions import TypeAlias


class ModbusSunspec(ICom):
    """
    ModbusSunspec class
    """
    
    
    # Address, Serial, Port, type, Slave_ID, verbose 
    Setup: TypeAlias = tuple[str | bytes | bytearray, int, int]
    
    def __init__(self, host, port, slave_id):
        """
        Constructor
        """
        self.host = host
        self.port = port
        self.unit_id = slave_id
        self.client = None
        
    def connect(self) -> None:
        self.client = client.SunSpecModbusClientDeviceTCP(slave_id=self.slave_id, ipaddr=self.host, ipport=self.port)
        self.client.scan()
        
    def disconnect(self) -> None:
        self.client.disconnect()
    
    def reconnect(self) -> None:
        self.disconnect() and self.connect()
    
    def read_harvest_data(self) -> dict:
        self.client.get_json(True)
    
    def get_harvest_data_type(self) -> str:
        return self.data_type 