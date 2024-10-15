import sunspec2.modbus.client as client
from sunspec2.modbus.client import SunSpecModbusClientError
from .ICom import ICom, HarvestDataType
import logging
from server.network.network_utils import NetworkUtils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ModbusSunspec(ICom):
    """
    ip: string, IP address of the Modbus TCP device,
    mac: string, MAC address of the Modbus TCP device,
    port: int, Port of the Modbus TCP device,
    device_type: string, solaredge, huawei or fronius etc...,
    slave_id: int, Modbus address of the Modbus TCP device
    """

    CONNECTION = "SUNSPEC"
    
    @property
    def IP(self) -> str:
        return "ip"
    
    @property
    def MAC(self) -> str:
        return "mac"
    
    @property
    def PORT(self) -> int:
        return "port"
    
    @property
    def DEVICE_TYPE(self) -> str:
        return "device_type"
    
    @property
    def SLAVE_ID(self) -> int:
        return "slave_id"
    

    @staticmethod
    def list_to_tuple(config: list) -> tuple:
        assert config[ICom.CONNECTION_IX] == ModbusSunspec.CONNECTION, "Invalid connection type"
        ip = config[1]
        mac = config[2]
        port = int(config[3])
        slave_id = int(config[4])
        return (config[ICom.CONNECTION_IX], ip, mac, port, slave_id)
    
    @staticmethod
    def dict_to_tuple(config: dict) -> tuple:
        assert config[ICom.CONNECTION_KEY] == ModbusSunspec.CONNECTION, "Invalid connection type"
        ip = config["host"]
        mac = config["mac"]
        port = int(config["port"])
        slave_id = int(config["address"])
        return (config[ICom.CONNECTION_KEY], ip, mac, port, slave_id)
    
    def __init__(self, 
                 ip: str, 
                 mac: str, 
                 port: int, 
                 slave_id: int, 
                 verbose: bool = False) -> None:
        """
        Constructor
        """
        self.ip = ip
        self.mac = mac
        self.port = port
        self.slave_id = slave_id
        self.client = None
        self.common = None
        self.inveter = None
        self.SN = None
        self.data_type = HarvestDataType.SUNSPEC.value
        
    def connect(self) -> bool:
        self.client = client.SunSpecModbusClientDeviceTCP(slave_id=self.slave_id, ipaddr=self.ip, ipport=self.port)
        self.mac = NetworkUtils.get_mac_from_ip(self.ip)
        self.client.scan()
        self.client.connect()
        
        logger.info("Models: %s", self.client.models)
        
        self.SN = self.client.models[0].SN
        
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

                # SF seems to not always be present so we try/except only SF readings
                payload["Hz"] = payload_verbose["Hz"]
                payload["W"] = payload_verbose["W"]
                payload["DCW"] = payload_verbose["DCW"]
                
                # SF seems to not always be present so we try to get with a default value of 1
                payload["Hz_SF"] = payload_verbose.get("Hz_SF", 1)
                payload["W_SF"] = payload_verbose.get("W_SF", 1)
                payload["DCW_SF"] = payload_verbose.get("DCW_SF", 1)

                return payload
        except Exception as e:
            logger.error("Error reading harvest data: %s", e)
            raise SunSpecModbusClientError(e)

    def get_harvest_data_type(self) -> str:
        return self.data_type

    def get_config(self):
        return {
            ICom.CONNECTION_KEY: ModbusSunspec.CONNECTION,
            self.IP: self.ip,
            self.MAC: self.mac,
            self.PORT: self.port,
            self.SLAVE_ID: self.slave_id
        }
        
    def get_profile(self):
        pass
    
    def _get_SN(self) -> str:
        return self.SN
    
    def clone(self, ip: str = None) -> 'ModbusSunspec':
        if ip is None:
            ip = self.ip
        return ModbusSunspec(ip, self.mac, self.port, self.slave_id)