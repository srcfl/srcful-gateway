from typing import Optional
from server.devices.Device import Device
from server.devices.inverters.common import INVERTER_CLIENT_NAME
from .ModbusTCP import ModbusTCP
from ..ICom import ICom
from pysolarmanv5 import PySolarmanV5
from server.network.network_utils import HostInfo, NetworkUtils
import logging
from server.devices.profile_keys import ProtocolKey
from server.devices.supported_devices.profiles import ModbusDeviceProfiles
from server.devices.profile_keys import FunctionCodeKey


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)



class ModbusSolarman(ModbusTCP):
    """
    ModbusSolarman device class
    
    Attributes:
        ip (str): The IP address or hostname of the device.
        mac (str, optional): The MAC address of the device. Defaults to "00:00:00:00:00:00" if not provided.
        sn (int): The serial number of the logger stick.
        port (int): The port number used for the Modbus connection.
        device_type (str): The type of the device (solaredge, huawei or fronius etc...).
        slave_id (int): The Modbus address of the device, typically used to identify the device on the network.
        verbose (int, optional): The verbosity level of the device. Defaults to 0.
    """
    
    CONNECTION = "SOLARMAN"
    
    @property
    def VERBOSE(self) -> str:
        return self.verbose_key()
    
    @staticmethod
    def verbose_key() -> str:
        return "verbose"
    
    @staticmethod
    def get_supported_devices():
        supported_devices = []
        for profile in ModbusDeviceProfiles().get_supported_devices():
            if profile.protocol.value == ProtocolKey.SOLARMAN.value:    
                obj = {
                    ModbusTCP.device_type_key(): profile.name,
                'display_name': profile.display_name,
                'protocol': profile.protocol.value
                }
                supported_devices.append(obj)
            
        return {ModbusSolarman.CONNECTION: supported_devices}
    
    
    @staticmethod
    def get_config_schema():
        return {
            **ModbusTCP.get_config_schema(),
            **Device.get_config_schema(ModbusSolarman.CONNECTION),  # needed to set the correct connection type as ModbuTCP is also a concrete inverter class
            ModbusTCP.sn_key(): "int - Serial number of the logger stick",
        }
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
        self.verbose = kwargs.get(self.verbose_key(), 0)

    def _connect(self, **kwargs) -> bool:
        
        self._create_client(**kwargs)
        
        try:
            if not self.client.sock:
                log.error("FAILED to open inverter: %s", self.get_config())
                return False
            if self.client.sock:
                self.mac = NetworkUtils.get_mac_from_ip(self.ip)
        except Exception as e:
            log.error("Error opening inverter: %s", self.get_config())
            return False
        
        registers: dict = None
        
        try:
            registers: dict = self.read_harvest_data(force_verbose=False)
        except Exception as e:
            log.error("Failed to connect to device. Initial register read failed: %s", self.get_config())
            return False
        
        valid_reading = bool(registers and len(registers) > 0)
        
        return bool(self.client.sock) and self.mac != NetworkUtils.INVALID_MAC and valid_reading


    def is_open(self) -> bool:
        try:
            return bool(self.client and self.client.sock)
        except Exception as e:
            log.error("Error checking if inverter is open: %s", self._get_type())
            log.error(e)
            return False
        
    def _is_valid(self) -> bool:
        return self.get_SN() is not None

    def _close(self) -> None:
        try:
            self.client.disconnect()
            self.client.sock = None
            log.info("Close -> Inverter disconnected successfully: %s", self._get_type())
        except Exception as e:
            log.error("Close -> Error disconnecting inverter: %s", self._get_type())
            log.error(e)

    def _disconnect(self) -> None:
        self._close()
        self._isTerminated = True

    def clone(self, ip: str = None) -> 'ModbusSolarman':
        config = self.get_config()
        if ip:
            config[self.IP] = ip

        return ModbusSolarman(**config)
    
    def get_SN(self) -> str:
        return str(self.sn)
    
    def get_client_name(self) -> str:
        return INVERTER_CLIENT_NAME + ".solarman." + self.get_name().lower()

    def get_config(self) -> dict:
        super_config = super().get_config()

        my_config = {
            self.SN: self.sn,
            self.VERBOSE: self.verbose
        }
        return {**super_config, **my_config}
    
    def _get_connection_type(self) -> str:
        return ModbusSolarman.CONNECTION
    
    def _create_client(self, **kwargs) -> None:
        try:
            self.client = PySolarmanV5(address=self.ip,
                            serial=self.sn,
                            port=self.port,
                            mb_slave_id=self.slave_id,
                            v5_error_correction=False,
                            verbose=self.verbose,
                            **kwargs)
        except Exception as e:
            log.error("Error creating client: %s", e)

    def _read_registers(self, function_code:FunctionCodeKey, scan_start:int, scan_range:int) -> list:
        resp = None

        if function_code == FunctionCodeKey.READ_INPUT_REGISTERS:
            resp = self.client.read_input_registers(register_addr=scan_start, quantity=scan_range)
        elif function_code == FunctionCodeKey.READ_HOLDING_REGISTERS:
            resp = self.client.read_holding_registers(register_addr=scan_start, quantity=scan_range)

        return resp

    def write_register(self, function_code: FunctionCodeKey, register: int, value: int) -> bool:
        raise NotImplementedError("Not implemented yet")
    

    def _clone_with_host(self, host: HostInfo) -> Optional[ICom]:

        if host.mac != self.mac:
            return None
        
        config = self.get_config()
        config[self.IP] = host.ip
        return ModbusSolarman(**config)