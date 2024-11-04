from typing import Optional
import sunspec2.modbus.client as client
from sunspec2.modbus.client import SunSpecModbusClientError

from server.devices.Device import Device
from server.devices.TCPDevice import TCPDevice
from ..ICom import ICom, HarvestDataType
import logging
from server.network.network_utils import HostInfo, NetworkUtils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ModbusSunspec(TCPDevice):
    """
    ModbusSunspec device class
    
    """

    CONNECTION = "SUNSPEC"
    
    @property
    def DEVICE_TYPE(self) -> str:
        return self.device_type_key()
    
    @staticmethod
    def device_type_key() -> str:
        return "device_type"
    
    @property
    def MAC(self) -> str:
        return self.mac_key()
    
    @staticmethod
    def mac_key() -> str:
        return "mac"
    
    @property
    def SLAVE_ID(self) -> str:
        return self.slave_id_key()
    
    @staticmethod
    def slave_id_key() -> str:
        return "slave_id"
    
    @property
    def SN(self) -> str:
        return self.sn_key()
    
    @staticmethod
    def sn_key() -> str:
        return "sn"
    
    @staticmethod
    def get_supported_devices():
        return {ModbusSunspec.CONNECTION: {'device_type': 'sunspec', 'display_name': 'SunSpec Device', 'protocol': 'modbus'}}
    
    @staticmethod
    def get_config_schema():
        """Returns the schema for the config and optional parameters of the ModbusSunspec device."""
        return {
            ModbusSunspec.mac_key(): "string - (Optional) MAC address of the device",
            ModbusSunspec.slave_id_key(): "int - Modbus address of the device",
            **TCPDevice.get_config_schema(),
        }
    
    def __init__(self, **kwargs) -> None:
        if "host" in kwargs:
            kwargs[self.ip_key()] = kwargs.pop("host")
        if "address" in kwargs:
            kwargs[self.slave_id_key()] = kwargs.pop("address")
        if "type" in kwargs:
            kwargs[self.device_type_key()] = kwargs.pop("type")


        ip = kwargs.get(self.ip_key(), None)
        port = kwargs.get(self.port_key(), None)

        TCPDevice.__init__(self, ip, port)

        self.mac = kwargs.get(self.mac_key(), NetworkUtils.INVALID_MAC)
        self.slave_id = kwargs.get(self.slave_id_key(), 1)
        self.sn = kwargs.get(self.sn_key(), None)
        self.client = None
        self.common = None
        self.inverter = None
        self.ac_model = None
        self.dc_model = None
        self.data_type = HarvestDataType.SUNSPEC
        
    def _connect(self, **kwargs) -> bool:
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
            
        return len(self.client.models) > 0 and self.mac != NetworkUtils.INVALID_MAC
       
    def _disconnect(self) -> None:
        self.client.disconnect()
           
    def is_open(self) -> bool:
        return bool(self.client.is_connected())
    
    def _read_harvest_data(self, force_verbose=False) -> dict:
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

    def get_harvest_data_type(self) -> HarvestDataType:
        return self.data_type

    def get_config(self):
        return {
            ICom.CONNECTION_KEY: ModbusSunspec.CONNECTION,
            **TCPDevice.get_config(self),
            self.MAC: self.mac,
            self.SLAVE_ID: self.slave_id,
            self.SN: self.get_SN()
        }
        
    def get_name(self) -> str:
        return "Sunspec"
    
    def clone(self) -> 'ICom':
        return ModbusSunspec(**self.get_config())
    
    def _clone_with_host(self, host: HostInfo) -> Optional[ICom]:

        if host.mac != self.mac:
            return None
        
        config = self.get_config()
        config[self.IP] = host.ip
        return ModbusSunspec(**config)
    
    def get_SN(self) -> str:
        return self.sn or self.mac