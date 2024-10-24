from typing import Optional
from .modbus import Modbus
from .ICom import ICom, HarvestDataType
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ModbusIOException
from pymodbus.pdu import ExceptionResponse
from pymodbus import pymodbus_apply_logging_config
from server.network.network_utils import NetworkUtils
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

pymodbus_apply_logging_config("INFO")

class ModbusTCP(Modbus):
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
    def get_config_schema():
        return {
            ModbusTCP.ip_key(): "string - IP address or hostname of the device",
            ModbusTCP.mac_key(): "string - (Optional) MAC address of the device",
            ModbusTCP.port_key(): "int - port of the device",
            ModbusTCP.device_type_key(): "string - type of the device",
            ModbusTCP.slave_id_key(): "int - Modbus address of the device",
        }

    # init but with kwargs
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
        # check if old keys are provided
        if "host" in kwargs:
            kwargs[self.ip_key()] = kwargs.pop("host")
            
        # get the kwargs, and default if not provided
        self.ip = kwargs.get(self.ip_key(), None)
        self.mac = kwargs.get(self.mac_key(), "00:00:00:00:00:00")
        self.port = kwargs.get(self.port_key(), None)
        self.client = None
        self.data_type = HarvestDataType.MODBUS_REGISTERS.value

    def _open(self, **kwargs) -> bool:
        if not self._is_terminated():
            self._create_client(**kwargs)
            if not self.client.connect():
                log.error("FAILED to open Modbus TCP device: %s", self._get_type())
            return bool(self.client.socket)
        else:
            return False

    def _is_open(self) -> bool:
        return bool(self.client) and bool(self.client.socket)
    
    def _is_valid(self) -> bool:
        return self.mac != "00:00:00:00:00:00"

    def _close(self) -> None:
        log.info("Closing client ModbusTCP %s", self._get_mac())
        self.client.close()

    def _terminate(self) -> None:
        self._close()
        self._isTerminated = True

    def _is_terminated(self) -> bool:
        return self._isTerminated

    def _clone(self, ip: str = None) -> 'ModbusTCP':
        if ip is None:
            ip = self._get_host()
            
        args = {
            self.ip_key(): ip,
            self.mac_key(): self._get_mac(),
            self.port_key(): self._get_port(),
            self.device_type_key(): self._get_type(),
            self.slave_id_key(): self._get_slave_id()
        }

        return ModbusTCP(**args)

    def _get_host(self) -> str:
        return self.ip
    
    def _get_mac(self) -> str:
        return self.mac

    def _get_port(self) -> int:
        return self.port

    def _get_type(self) -> str:
        return self.device_type

    def _get_slave_id(self) -> int:
        return self.slave_id
    
    def _get_SN(self) -> str:
        return self.mac

    def _get_config_dict(self) -> dict:
        return {
            ICom.CONNECTION_KEY: ModbusTCP.CONNECTION,
            self.DEVICE_TYPE: self._get_type(),
            self.MAC: self._get_mac(),
            self.SLAVE_ID: self._get_slave_id(),
            self.IP: self._get_host(),
            self.PORT: self._get_port(),
            self.SN: self._get_SN()
        }

    def _create_client(self, **kwargs) -> None:
        self.client =  ModbusClient(host=self._get_host(),
                                    port=self._get_port(), 
                                    unit_id=self._get_slave_id(),
                                    **kwargs
        )
        self.mac = NetworkUtils.get_mac_from_ip(self._get_host())
    def _read_registers(self, operation, scan_start, scan_range) -> list:
        resp = None
        
        if operation == 0x04:
            resp = self.client.read_input_registers(scan_start, scan_range, slave=self._get_slave_id())
        elif operation == 0x03:
            resp = self.client.read_holding_registers(scan_start, scan_range, slave=self._get_slave_id())

        # Not sure why read_input_registers dose not raise an ModbusIOException but rather returns it
        # We solve this by raising the exception manually
        if isinstance(resp, ModbusIOException):
            raise ModbusIOException("Exception occurred while reading registers")
        
        return resp.registers
    
    def write_registers(self, starting_register, values) -> None:
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
    
