from .modbus import Modbus
from .ICom import ICom
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.pdu import ExceptionResponse
from pymodbus.exceptions import ModbusIOException
from pymodbus import pymodbus_apply_logging_config
from typing_extensions import TypeAlias
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
    type: string, solaredge, huawei or fronius etc...,
    address: int, Modbus address of the inverter,
    """

    CONNECTION = "RTU"

    def list_to_tuple(config: list) -> tuple:
        assert config[ICom.CONNECTION_IX] == ModbusRTU.CONNECTION, "Invalid connection type"
        port = config[1]
        baudrate = int(config[2])
        bytesize = int(config[3])
        parity = config[4]
        stopbits = float(config[5])
        inverter_type = config[6]
        slave_id = int(config[7])
        return (config[0], port, baudrate, bytesize, parity, stopbits, inverter_type, slave_id)
    
    def dict_to_tuple(config: dict) -> tuple:
        assert config[ICom.CONNECTION_KEY] == ModbusRTU.CONNECTION, "Invalid connection type"
        serial_port = config["port"]
        baudrate = int(config["baudrate"])
        bytesize = int(config["bytesize"])
        parity = config["parity"]
        stopbits = float(config["stopbits"])
        inverter_type = config["type"]
        slave_id = int(config["address"])
        return (config[ICom.CONNECTION_KEY], serial_port, baudrate, bytesize, parity, stopbits, inverter_type, slave_id)


    Setup: TypeAlias = tuple[str, int, int, str, float, str, int]

    def __init__(self, setup: Setup):
        log.info("Creating with: %s" % str(setup))
        self.setup = setup
        self.client = None
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
            
        return ModbusRTU((host, self._get_baudrate(),
                            self._get_bytesize(), self._get_parity(),
                            self._get_stopbits(), self._get_type(), self._get_address()))

    def _get_host(self) -> str:
        return self.setup[0]

    def _get_baudrate(self) -> int:
        return int(self.setup[1])

    def _get_bytesize(self) -> int:
        return self.setup[2]

    def _get_parity(self) -> str:
        return self.setup[3]

    def _get_stopbits(self) -> int:
        return self.setup[4]

    def _get_type(self) -> str:
        return self.setup[5]

    def _get_address(self) -> int:
        return self.setup[6]

    def _get_config(self) -> tuple[str, str, int, int, str, float, str, int]:
        return (
            ModbusRTU.CONNECTION,
            self._get_host(),
            self._get_baudrate(),
            self._get_bytesize(),
            self._get_parity(),
            self._get_stopbits(),
            self._get_type(),
            self._get_address(),
        )

    def _get_config_dict(self) -> dict:
        return {
            ICom.CONNECTION_KEY: ModbusRTU.CONNECTION,
            "type": self._get_type(),
            "address": self._get_address(),
            "port": self._get_host(),
            "baudrate": self._get_baudrate(),
            "bytesize": self._get_bytesize(),
            "parity": self._get_parity(),
            "stopbits": self._get_stopbits(),
        }
    
    def _get_backend_type(self) -> str:
        return self._get_type().lower()
    
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
            resp = self.client.read_input_registers(scan_start, scan_range, slave=self._get_address())
        elif operation == 0x03:
            resp = self.client.read_holding_registers(scan_start, scan_range, slave=self._get_address())

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
            starting_register, values, slave=self._get_address()
        )
        log.debug("OK - Writing Holdings: %s - %s", str(starting_register),  str(values))
        
        if isinstance(resp, ExceptionResponse):
            raise Exception("writeRegisters() - ExceptionResponse: " + str(resp))
        return resp
