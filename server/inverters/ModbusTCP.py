from .modbus import Modbus
from .ICom import ICom, HarvestDataType
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.pdu import ExceptionResponse
from pymodbus.exceptions import ModbusIOException
from pymodbus import pymodbus_apply_logging_config
from typing_extensions import TypeAlias
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

pymodbus_apply_logging_config("INFO")


class ModbusTCP(Modbus):

    """
    ip: string, IP address of the inverter,
    mac: string, MAC address of the inverter,
    port: int, Port of the inverter,
    type: string, solaredge, huawei or fronius etc...,
    address: int, Modbus address of the inverter
    """


    CONNECTION = "TCP"

    @staticmethod
    def list_to_tuple(config: list) -> tuple:
        assert config[ICom.CONNECTION_IX] == ModbusTCP.CONNECTION, "Invalid connection type"
        ip = config[1]
        mac = config[2]
        port = int(config[3])
        inverter_type = config[4]
        slave_id = int(config[5])
        return (config[ICom.CONNECTION_IX], ip, mac, port, inverter_type, slave_id)
    
    @staticmethod
    def dict_to_tuple(config: dict) -> tuple:
        assert config[ICom.CONNECTION_KEY] == ModbusTCP.CONNECTION, "Invalid connection type"
        ip = config["host"]
        mac = config["mac"]
        port = int(config["port"])
        inverter_type = config["type"]
        slave_id = int(config["address"])
        return (config[ICom.CONNECTION_KEY], ip, mac, port, inverter_type, slave_id)
        
    Setup: TypeAlias = tuple[str | bytes | bytearray, str, int, str, int]

    def __init__(self, setup: Setup) -> None:
        log.info("Creating with: %s" % str(setup))
        self.setup = setup
        self.client = None
        self.data_type = HarvestDataType.MODBUS_REGISTERS.value
        super().__init__()

    def _open(self, **kwargs) -> bool:
        if not self._is_terminated():
            self._create_client(**kwargs)
            if not self.client.connect():
                log.error("FAILED to open inverter: %s", self._get_type())
            return bool(self.client.socket)
        else:
            return False

    def _is_open(self) -> bool:
        return bool(self.client) and bool(self.client.socket)

    def _close(self) -> None:
        log.info("Closing client ModbusTCP")
        self.client.close()

    def _terminate(self) -> None:
        self._close()
        self._isTerminated = True

    def _is_terminated(self) -> bool:
        return self._isTerminated

    def _clone(self, host: str = None) -> 'ModbusTCP':
        if host is None:
            host = self._get_host()

        return ModbusTCP((host, self._get_mac(), self._get_port(),
                            self._get_type(), self._get_address()))

    def _get_host(self) -> str:
        return self.setup[0]
    
    def _get_mac(self) -> str:
        return self.setup[1]

    def _get_port(self) -> int:
        return self.setup[2]

    def _get_type(self) -> str:
        return self.setup[3].lower()

    def _get_address(self) -> int:
        return self.setup[4]

    def _get_config(self) -> tuple[str, str, int, str, int]:
        return (
            ModbusTCP.CONNECTION,
            self._get_host(),
            self._get_mac(),
            self._get_port(),
            self._get_type(),
            self._get_address(),
        )

    def _get_config_dict(self) -> dict:
        return {
            ICom.CONNECTION_KEY: ModbusTCP.CONNECTION,
            "type": self._get_type(),
            "mac": self._get_mac(),
            "address": self._get_address(),
            "host": self._get_host(),
            "port": self._get_port(),
        }

    def _create_client(self, **kwargs) -> None:
        self.client =  ModbusClient(host=self._get_host(),
                                    port=self._get_port(), 
                                    unit_id=self._get_address(),
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
    