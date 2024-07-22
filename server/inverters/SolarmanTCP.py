from .inverter import Inverter
from pysolarmanv5 import PySolarmanV5
from typing_extensions import TypeAlias
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class SolarmanTCP(Inverter):
    """
    ip: string, IP address of the inverter,
    port: int, Port of the inverter,
    type: string, solaredge, huawei or fronius etc...,
    address: int, Modbus address of the inverter
    """

    # Address, Serial, Port, Slave_ID, verbose 
    Setup: TypeAlias = tuple[str | bytes | bytearray, int, int, str, int]

    def __init__(self, setup: Setup) -> None:
        log.info("Creating with: %s" % str(setup))
        self.setup = setup
        super().__init__()

    def open(self, **kwargs) -> bool:
        if not self.is_terminated():
            self._create_client(**kwargs)
            if not self.client.sock:
                log.error("FAILED to open inverter: %s", self.get_type())
            return bool(self.client.sock)
        else:
            return False

    def is_open(self) -> bool:
        return bool(self.client.sock)

    def close(self) -> None:
        self.client.disconnect()

    def terminate(self) -> None:
        self.close()
        self._isTerminated = True

    def is_terminated(self) -> bool:
        return self._isTerminated

    def clone(self, host: str = None):
        if host is None:
            host = self.get_host()
        return PySolarmanV5(address=host,
                            serial=self.get_serial(), 
                            port=self.get_port(), 
                            mb_slave_id=self.get_address(), 
                            v5_error_correction=False)

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

    def get_config(self) -> tuple[str, str, int, str, int]:
        return (
            "SOLARMAN",
            self.get_host(),
            self.get_serial(),
            self.get_port(),
            self.get_type(),
            self.get_address(),
        )

    def get_config_dict(self) -> dict:
        return {
            "connection": "SOLARMAN",
            "type": self.get_type(),
            "serial": self.get_serial(),
            "address": self.get_address(),
            "host": self.get_host(),
            "port": self.get_port(),
        }

    def get_backend_type(self) -> str:
        return self.get_type().lower()
    
    def _create_client(self, **kwargs) -> None:
        self.client = PySolarmanV5(address=self.get_host(), 
                            serial=self.get_serial(), 
                            port=self.get_port(), 
                            mb_slave_id=self.get_address(), 
                            v5_error_correction=False, 
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
