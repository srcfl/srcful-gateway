from .modbus import Modbus
from pysolarmanv5 import PySolarmanV5
from typing_extensions import TypeAlias
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class ModbusSolarman(Modbus):
    """
    ip: string, IP address of the inverter,
    serial: int, Serial number of the logger stick,
    port: int, Port of the inverter,
    type: string, solaredge, huawei or fronius etc...,
    address: int, Modbus address of the inverter
    verbose: int, 0 or 1 for verbose logging

    """

    # Address, Serial, Port, type, Slave_ID, verbose 
    Setup: TypeAlias = tuple[str | bytes | bytearray, int, int, str, int, int]

    def __init__(self, setup: Setup) -> None:
        log.info("Creating with: %s" % str(setup))
        self.setup = setup
        self.client = None
        super().__init__()

    def _open(self, **kwargs) -> bool:
        if not self._is_terminated():
            self._create_client(**kwargs)
            if not self.client.sock:
                log.error("FAILED to open inverter: %s", self.get_type())
            return bool(self.client.sock)
        else:
            return False

    def _is_open(self) -> bool:
        return bool(self.client.sock)

    def _close(self) -> None:
        try:
            self.client.disconnect()
            self.client.sock = None
            log.info("Close -> Inverter disconnected successfully: %s", self.get_type())
        except Exception as e:
            log.error("Close -> Error disconnecting inverter: %s", self.get_type())
            log.error(e)

    def _terminate(self) -> None:
        self._close()
        self._isTerminated = True

    def _is_terminated(self) -> bool:
        return self._isTerminated

    def _clone(self, host: str = None):
        if host is None:
            host = self.get_host()

        return ModbusSolarman(
            (host, 
             self.get_serial(), 
             self.get_port(), 
             self.get_type(), 
             self.get_address(), 
             self.setup[5])
        )

    def get_host(self) -> str:
        return self.setup[0]

    def get_serial(self) -> int:
        return self.setup[1]
    
    def get_port(self) -> int:
        return self.setup[2]

    def get_type(self) -> str:
        return self.setup[3]
    
    def get_address(self) -> int:
        return self.setup[4]

    def _get_config(self) -> tuple[str, str, int, str, int]:
        return (
            "SOLARMAN",
            self.get_host(),
            self.get_serial(),
            self.get_port(),
            self.get_type(),
            self.get_address(),
        )

    def _get_config_dict(self) -> dict:
        return {
            "connection": "SOLARMAN",
            "type": self.get_type(),
            "serial": self.get_serial(),
            "address": self.get_address(),
            "host": self.get_host(),
            "port": self.get_port(),
        }

    def _get_backend_type(self) -> str:
        return self.get_type().lower()
    
    def _create_client(self, **kwargs) -> None:
        self.client = PySolarmanV5(address=self.get_host(), 
                            serial=self.get_serial(), 
                            port=self.get_port(), 
                            mb_slave_id=self.get_address(), 
                            v5_error_correction=False,
                            verbose=self.setup[5],
                            **kwargs)

    def _read_registers(self, operation, scan_start, scan_range) -> list:
        resp = None

        if operation == 0x04:
            resp = self.client.read_input_registers(register_addr=scan_start, quantity=scan_range)
        elif operation == 0x03:
            resp = self.client.read_holding_registers(register_addr=scan_start, quantity=scan_range)

        return resp

    def write_register(self, operation, register, value) -> bool:
        raise NotImplementedError("Not implemented yet")
