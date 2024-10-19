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
    port: string, Serial port used for communication,
    baudrate: int, Bits per second,
    bytesize: int, Number of bits per byte 7-8,
    parity: string, 'E'ven, 'O'dd or 'N'one,
    stopbits: float, Number of stop bits 1, 1.5, 2,
    device_type: string, solaredge, huawei or fronius etc...,
    slave_id: int, Modbus address of the inverter,
    """

    CONNECTION = "RTU"
    
    @property
    def PORT(self) -> str:
        return "port"
    
    @property
    def BAUD_RATE(self) -> int:
        return "baudrate"   
    
    @property
    def BYTESIZE(self) -> int:
        return "bytesize"
    
    @property
    def PARITY(self) -> str:
        return "parity"
    
    @property
    def STOPBITS(self) -> float:
        return "stopbits"
    
    @property
    def DEVICE_TYPE(self) -> str:
        return "device_type"
    
    @property
    def SLAVE_ID(self) -> int:
        return "slave_id"
    

    def __init__(self, 
                 port: str = None, 
                 baudrate: int = None, 
                 bytesize: int = None, 
                 parity: str = None, 
                 stopbits: float = None,
                 device_type: str = None,
                 slave_id: int = None):
        log.info("Creating with: %s, %s, %s, %s, %s, %s, %s", port, baudrate, bytesize, parity, stopbits, device_type, slave_id)
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.device_type = device_type
        self.slave_id = slave_id
        self.client = None
        self.data_type = HarvestDataType.MODBUS_REGISTERS.value
        super().__init__()

    def _open(self, **kwargs) -> bool:
        self._create_client(**kwargs)
        if not self.client.connect():
            log.error("FAILED to open inverter: %s", self._get_type())
            return bool(self.client.socket)
        else:
            return False

    def _is_open(self) -> bool:
        return bool(self.client.socket)
    
    def _close(self) -> None:
        self.client.close()

    def _terminate(self) -> None:
        self._close()
        self._isTerminated = True

    def _is_terminated(self) -> bool:
        return self._isTerminated

    def _clone(self, host: str = None) -> 'ModbusRTU':
        if host is None:
            host = self._get_host()
            
        return ModbusRTU(host, 
                        self._get_baudrate(),
                        self._get_bytesize(), 
                        self._get_parity(),
                        self._get_stopbits(), 
                        self._get_type(), 
                        self._get_slave_id())

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
    
    def _get_SN(self) -> str:
        return "N/A"

    def _get_config(self) -> tuple[str, str, int, int, str, float, str, int]:
        return (
            ModbusRTU.CONNECTION,
            self._get_host(),
            self._get_baudrate(),
            self._get_bytesize(),
            self._get_parity(),
            self._get_stopbits(),
            self._get_type(),
            self._get_slave_id(),
        )

    def _get_config_dict(self) -> dict:
        return {
            ICom.CONNECTION_KEY: ModbusRTU.CONNECTION,
            self.DEVICE_TYPE: self._get_type(),
            self.SLAVE_ID: self._get_slave_id(),
            self.PORT: self._get_host(),
            self.BAUD_RATE: self._get_baudrate(),
            self.BYTESIZE: self._get_bytesize(),
            self.PARITY: self._get_parity(),
            self.STOPBITS: self._get_stopbits(),
        }
    
    def _create_client(self, **kwargs) -> None:
        self.client = ModbusClient(
            method="rtu",
            port=self._get_host(),
            baudrate=self._get_baudrate(),
            bytesize=self._get_bytesize(),
            parity=self._get_parity(),
            stopbits=self._get_stopbits(),
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

    def is_valid(self) -> bool:
        raise NotImplementedError("is_valid is not implemented for ModbusRTU")