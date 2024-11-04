from typing import Optional
from server.devices.TCPDevice import TCPDevice
from server.devices.profile_keys import OperationKey
from .modbus import Modbus
from ..ICom import ICom, HarvestDataType
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ModbusIOException
from pymodbus.pdu import ExceptionResponse
from pymodbus import pymodbus_apply_logging_config
from server.network.network_utils import HostInfo, NetworkUtils
from server.devices.supported_devices.profiles import ModbusDeviceProfiles
import logging
from server.devices.profile_keys import ProtocolKey


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

pymodbus_apply_logging_config("INFO")

class ModbusTCP(Modbus, TCPDevice):
    """
    ModbusTCP device class.

    Attributes:
        ip (str): The IP address or hostname of the device.
        mac (str, optional): The MAC address of the device. Defaults to "00:00:00:00:00:00" if not provided.
        port (int): The port number used for the Modbus connection.
        device_type (str): The type of the device (e.g., solaredge, huawei, fronius).
        slave_id (int): The Modbus address of the device, typically used to identify the device on the network.
    """

    CONNECTION = "TCP"
    
  
    @staticmethod
    def ip_key() -> str:
        return "ip"

    @property
    def MAC(self) -> str:
        return self.mac_key()
    
    @staticmethod
    def mac_key() -> str:
        return "mac"
    
    @staticmethod
    def port_key() -> str:
        return "port"
    
    @staticmethod
    def get_supported_devices():
        supported_devices = []
        for profile in ModbusDeviceProfiles().get_supported_devices():
            if profile.protocol.value == ProtocolKey.MODBUS.value:    
                obj = {
                    ModbusTCP.device_type_key(): profile.name,
                'display_name': profile.display_name,
                'protocol': profile.protocol.value
            }
                supported_devices.append(obj)
            
        return {ModbusTCP.CONNECTION: supported_devices}
    
    @staticmethod
    def get_config_schema():
        return {
            **Modbus.get_config_schema(ModbusTCP.CONNECTION),
            ModbusTCP.mac_key(): "string - (Optional) MAC address of the device",
            ModbusTCP.device_type_key(): "string - type of the device",
            ModbusTCP.slave_id_key(): "int - Modbus address of the device",
        }

    # init but with kwargs
    def __init__(self, **kwargs) -> None:
        Modbus.__init__(self, **kwargs)
        
        # check if old keys are provided
        if "host" in kwargs:
            kwargs[self.ip_key()] = kwargs.pop("host")
            
        # get the kwargs, and default if not provided
        ip = kwargs.get(self.ip_key(), None)
        port = kwargs.get(self.port_key(), None)    
        TCPDevice.__init__(self, ip, port)

        self.mac = kwargs.get(self.mac_key(), NetworkUtils.INVALID_MAC)
        self.client = None
        self.data_type = HarvestDataType.MODBUS_REGISTERS

    def _connect(self, **kwargs) -> bool:
        self._create_client(**kwargs)
        if not self.client.connect():
            log.error("FAILED to open Modbus TCP device: %s", self._get_type())
        if self.client.socket:
            self.mac = NetworkUtils.get_mac_from_ip(self.ip)
        return bool(self.client.socket) and self.mac != NetworkUtils.INVALID_MAC
        
    def _get_type(self) -> str:
        return self.device_type

    def is_open(self) -> bool:
        return bool(self.client) and bool(self.client.socket)

    def _close(self) -> None:
        log.info("Closing client ModbusTCP %s", self.mac)
        self.client.close()

    def _disconnect(self) -> None:
        self._close()

    def clone(self, ip: str | None = None) -> 'ModbusTCP':
        config = self.get_config()
        if ip:
            config[self.IP] = ip

        return ModbusTCP(**config)

    def get_config(self) -> dict:

        return {
            **Modbus.get_config(self),
            **TCPDevice.get_config(self),
            self.MAC: self.mac,
        }
    
    def _get_connection_type(self) -> str:
        return ModbusTCP.CONNECTION
    
    def get_SN(self) -> str:
        # TODO: get the serial number from the device use mac for now
        return self.mac

    def _create_client(self, **kwargs) -> None:
        self.client =  ModbusClient(host=self.ip, port=self.port, unit_id=self.slave_id, **kwargs)

    def _read_registers(self, operation:OperationKey, scan_start, scan_range) -> list:
        resp = None
        
        if operation == OperationKey.READ_INPUT_REGISTERS:
            resp = self.client.read_input_registers(scan_start, scan_range, slave=self.slave_id)
        elif operation == OperationKey.READ_HOLDING_REGISTERS:
            resp = self.client.read_holding_registers(scan_start, scan_range, slave=self.slave_id)

        # Not sure why read_input_registers dose not raise an ModbusIOException but rather returns it
        # We solve this by raising the exception manually
        if isinstance(resp, ModbusIOException):
            raise ModbusIOException("Exception occurred while reading registers")
        
        return resp.registers
    
    def write_registers(self, starting_register, values) -> bool:
        """
        Write a range of holding registers from a start address
        """
        resp = self.client.write_registers(
            starting_register, values, slave=self._get_slave_id()
        )
        log.debug("OK - Writing Holdings: %s - %s", str(starting_register),  str(values))
        
        if isinstance(resp, ExceptionResponse):
            raise Exception("writeRegisters() - ExceptionResponse: " + str(resp))
        return resp
    
    def _clone_with_host(self, host: HostInfo) -> Optional[ICom]:

        if host.mac != self.mac:
            return None
        
        config = self.get_config()
        config[self.IP] = host.ip
        return ModbusTCP(**config)
    
