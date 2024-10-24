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
        return self.ip_key()
    
    @staticmethod
    def ip_key() -> str:
        return "ip"

    @property
    def MAC(self) -> str:
        return self.mac_key()
    
    @staticmethod
    def mac_key() -> str:
        return "mac"
    
    @property
    def PORT(self) -> str:
        return self.port_key()
    
    @staticmethod
    def port_key() -> str:
        return "port"
    
    
    @staticmethod
    def device_type_key() -> str:
        return "device_type"

    @property
    def SLAVE_ID(self) -> str:
        return self.slave_id_key()
    
    @staticmethod
    def slave_id_key() -> str:
        return "slave_id"
    
    @staticmethod
    def get_config_schema():
        return {
            ICom.CONNECTION_KEY: ModbusSunspec.CONNECTION,
            ModbusSunspec.ip_key(): "string, IP address or hostname of the device",
            ModbusSunspec.mac_key(): "string, MAC address of the device",
            ModbusSunspec.port_key(): "int, port of the device",
            ModbusSunspec.slave_id_key(): "int, Modbus address of the device",
        }
    
    def __init__(self, **kwargs) -> None:
        if "host" in kwargs:
            kwargs[self.ip_key()] = kwargs.pop("host")
        if "address" in kwargs:
            kwargs[self.slave_id_key()] = kwargs.pop("address")
        if "type" in kwargs:
            kwargs[self.device_type_key()] = kwargs.pop("type")

        self.ip = kwargs.get(self.ip_key(), None)
        self.mac = kwargs.get(self.mac_key(), "00:00:00:00:00:00")
        self.port = kwargs.get(self.port_key(), None)
        self.slave_id = kwargs.get(self.slave_id_key(), 1)
        self.sn = kwargs.get(self.SN, None)
        self.client = None
        self.common = None
        self.inverter = None
        self.ac_model = None
        self.dc_model = None
        self.data_type = HarvestDataType.SUNSPEC.value
        
    def connect(self) -> bool:
        self.client = client.SunSpecModbusClientDeviceTCP(slave_id=self.slave_id, ipaddr=self.ip, ipport=self.port)
        self.mac = NetworkUtils.get_mac_from_ip(self.ip)
        self.client.scan()
        self.client.connect()
        
        logger.info("Models: %s", self.client.models)
        
        try:
            self.sn = self.client.common[0].SN.value
        except KeyError:
            logger.warning("Could not get serial number, using MAC address as fallback")
            self.sn = NetworkUtils.get_mac_from_ip(self.ip)

        if 'inverter' in self.client.models:
            self.inverter = self.client.inverter[0]
            
        if 'DERMeasureAC' in self.client.models:
            self.ac_model = self.client.DERMeasureAC[0]
        elif 701 in self.client.models:
            self.ac_model = self.client.models[701][0]
            
        if 'DERMeasureDC' in self.client.models:
            self.dc_model = self.client.DERMeasureDC[0]
        elif 714 in self.client.models:
            self.dc_model = self.client.models[714][0]
            
        return len(self.client.models) > 0
    
    def is_valid(self) -> bool:
        return self.get_SN() is not None and self.mac != "00:00:00:00:00:00"
    
    def disconnect(self) -> None:
        self.client.disconnect()
    
    def reconnect(self) -> bool:
        return self.disconnect() and self.connect()
        
    def is_open(self) -> bool:
        return bool(self.client.is_connected())
    
    def read_harvest_data(self, force_verbose=False) -> dict:
        try:
            if self.inverter is not None:
                self.inverter.read()
            if self.ac_model is not None:
                self.ac_model.read()
            if self.dc_model is not None:
                self.dc_model.read()
            
            if force_verbose:
                payload_verbose = self.client.get_dict()
                return payload_verbose
            else:
                
                payload_verbose = {}
                
                # the inverter would include W, Hz, and DCW, but it is not always available
                if self.inverter is not None:
                    payload_verbose = self.inverter.get_dict()
                else: 
                    if self.ac_model is not None:
                        payload_verbose = {**payload_verbose, **self.ac_model.get_dict()}
                    if self.dc_model is not None:
                        payload_verbose = {**payload_verbose, **self.dc_model.get_dict()}
                
                payload = {}
                
                # Get value and scale factor, if not present, set to 0 and 1 respectively (should not happen for Hz, W and DCW)
                payload["Hz"] = payload_verbose.get("Hz", 0)
                payload["Hz_SF"] = payload_verbose.get("Hz_SF", 1)
                payload["W"] = payload_verbose.get("W", 0)
                payload["W_SF"] = payload_verbose.get("W_SF", 1)
                payload["DCW"] = payload_verbose.get("DCW", 0)
                payload["DCW_SF"] = payload_verbose.get("DCW_SF", 1)

                return payload
        except Exception as e:
            logger.error("Error reading data: %s", e)
            raise SunSpecModbusClientError(e)

    def get_harvest_data_type(self) -> str:
        return self.data_type

    def get_config(self):
        return {
            ICom.CONNECTION_KEY: ModbusSunspec.CONNECTION,
            self.IP: self.ip,
            self.MAC: self.mac,
            self.PORT: self.port,
            self.SLAVE_ID: self.slave_id,
            self.SN: self.get_SN()
        }
        
    def get_profile(self):
        pass
    
    def clone(self, ip: str = None) -> 'ModbusSunspec':
        if ip is None:
            ip = self.ip
        return ModbusSunspec(ip, self.mac, self.port, self.slave_id)
    
    def find_device(self) -> 'ICom':
        port = self.get_config()[NetworkUtils.PORT_KEY] # get the port from the previous inverter config
        hosts = NetworkUtils.get_hosts([int(port)], 0.01)
        
        if len(hosts) > 0:
            for host in hosts:
                if host[NetworkUtils.MAC_KEY] == self.get_config()[NetworkUtils.MAC_KEY]:
                    return self.clone(host[NetworkUtils.IP_KEY])
        return None
    
    def get_SN(self) -> str:
        return self.sn