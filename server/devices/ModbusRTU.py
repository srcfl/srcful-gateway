from typing import Optional
from .modbus import Modbus
from .ICom import ICom, HarvestDataType
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.pdu import ExceptionResponse
from pymodbus.exceptions import ModbusIOException
from pymodbus import pymodbus_apply_logging_config
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

pymodbus_apply_logging_config("INFO")


class ModbusRTU(Modbus):
    """
    ModbusRTU device class
    
    Attributes:
        port (str): The serial port used for communication.
        baudrate (int): The bits per second.
        bytesize (int): The number of bits per byte (7-8).
        parity (str): The parity ('E'ven, 'O'dd or 'N'one).
        stopbits (float): The number of stop bits (1, 1.5, 2).
        device_type (str): The type of the device (solaredge, huawei or fronius etc...).
        slave_id (int): The Modbus address of the device.
    """

    CONNECTION = "RTU"
    
    @property
    def PORT(self) -> str:
        return "port"
    
    @staticmethod
    def port_key() -> str:
        return "port"
    
    @property
    def BAUD_RATE(self) -> str:
        return self.baud_rate_key()   
    
    @staticmethod
    def baud_rate_key() -> str:
        return "baudrate"
    
    @property
    def BYTESIZE(self) -> str:
        return self.bytesize_key()
    
    @staticmethod
    def bytesize_key() -> str:
        return "bytesize"
    
    @property
    def PARITY(self) -> str:
        return self.parity_key()
    
    @staticmethod
    def parity_key() -> str:
        return "parity"
    
    @property
    def STOPBITS(self) -> str:
        return self.stopbits_key()
    
    @staticmethod
    def stopbits_key() -> str:
        return "stopbits"
    
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
            ModbusRTU.baud_rate_key(): "string - baudrate of the device",
            ModbusRTU.bytesize_key(): "string - bytesize of the device",
            ModbusRTU.port_key(): "int - port of the device",
            ModbusRTU.parity_key(): "string - parity of the device",
            ModbusRTU.stopbits_key(): "float - stopbits of the device",
            ModbusRTU.device_type_key(): "string - type of the device",
            ModbusRTU.slave_id_key(): "int - Modbus address of the device",
        }
    
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
        self.port = kwargs.get(self.port_key(), None)
        self.baudrate = kwargs.get(self.baud_rate_key(), None)
        self.bytesize = kwargs.get(self.bytesize_key(), None)
        self.parity = kwargs.get(self.parity_key(), None)
        self.stopbits = kwargs.get(self.stopbits_key(), None)
        self.slave_id = kwargs.get(self.slave_id_key(), None)
        self.client = None
        self.data_type = HarvestDataType.MODBUS_REGISTERS.value
        
        


    def _open(self, **kwargs) -> bool:
        self._create_client(**kwargs)
        if not self.client.connect():
            log.error("FAILED to open inverter: %s", self._get_type())
            return bool(self.client.socket)
        else:
            return False

    def is_open(self) -> bool:
        return bool(self.client.socket)
    
    def _close(self) -> None:
        self.client.close()

    def _disconnect(self) -> None:
        self._close()


    def clone(self, host: str = None) -> 'ModbusRTU':
        if host is None:
            host = self._get_host()
            
        return ModbusRTU(self.port, 
                        self.baudrate,
                        self.bytesize, 
                        self.parity,
                        self.stopbits, 
                        self.device_type, 
                        self.slave_id)

    def _get_host(self) -> str:
        return self.port

    def _get_baudrate(self) -> int:
        return self.baudrate

    def _get_bytesize(self) -> int:
        return self.bytesize

    def _get_parity(self) -> str:
        return self.parity

    def _get_stopbits(self) -> int:
        return self.stopbits

    def _get_type(self) -> str:
        return self.device_type

    def _get_slave_id(self) -> int:
        return self.slave_id
    
    def find_device(self) -> 'ICom':
        raise NotImplementedError("find_device is not implemented for ModbusRTU")
    
    def get_SN(self) -> str:
        return "N/A"

    def get_config(self) -> dict:
        super_config = super().get_config()

        my_config = {
            ICom.CONNECTION_KEY: ModbusRTU.CONNECTION,
            self.SLAVE_ID: self.slave_id,
            self.PORT: self.port,
            self.BAUD_RATE: self.baudrate,
            self.BYTESIZE: self.bytesize,
            self.PARITY: self.parity,
            self.STOPBITS: self.stopbits,
        }
        return {**super_config, **my_config}
    
    def _create_client(self, **kwargs) -> None:
        self.client = ModbusClient( 
            method="rtu",
            port=self.port,
            baudrate=self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
            stopbits=self.stopbits,
            **kwargs
        )

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

    def _is_valid(self) -> bool:
        raise NotImplementedError("_is_valid is not implemented for ModbusRTU")