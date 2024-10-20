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
    ip: string, IP address of the Modbus TCP device,
    mac: string, MAC address of the Modbus TCP device,
    port: int, Port of the Modbus TCP device,
    device_type: string, solaredge, huawei or fronius etc...,
    address: int, Modbus address of the Modbus TCP device
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
    
    @property
    def DEVICE_TYPE(self) -> str:
        return self.device_type_key()
    
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
            ModbusTCP.ip_key(): "string, IP address or hostname of the device",
            ModbusTCP.mac_key(): "optional, string, MAC address of the device",
            ModbusTCP.port_key(): "int, port of the device",
            ModbusTCP.device_type_key(): "string, type of the device",
            ModbusTCP.slave_id_key(): "int, Modbus address of the device",
        }

    def __init__(self,
                 ip: Optional[str] = None,
                 mac: str = "00:00:00:00:00:00",
                 port: Optional[int] = None, 
                 device_type: Optional[str] = None, 
                 slave_id: Optional[int] = None) -> None:
        log.info("Creating with: %s %s %s %s %s", ip, mac, port, device_type, slave_id)
        self.ip = ip
        self.mac = mac
        self.port = port
        self.device_type = device_type
        self.slave_id = slave_id
        self.client = None
        self.data_type = HarvestDataType.MODBUS_REGISTERS.value
        super().__init__()

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

        return ModbusTCP(ip, self._get_mac(), self._get_port(),
                            self._get_type(), self._get_slave_id())

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

    def _get_config(self) -> tuple[str, str, int, str, int]:
        return (
            ModbusTCP.CONNECTION,
            self._get_host(),
            self._get_mac(),
            self._get_port(),
            self._get_type(),
            self._get_slave_id(),
        )

    def _get_config_dict(self) -> dict:
        return {
            ICom.CONNECTION_KEY: ModbusTCP.CONNECTION,
            self.DEVICE_TYPE: self._get_type(),
            self.MAC: self._get_mac(),
            self.SLAVE_ID: self._get_slave_id(),
            self.IP: self._get_host(),
            self.PORT: self._get_port(),
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
    