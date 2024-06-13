from .inverter import Inverter
from pysolarmanv5 import PySolarmanV5
from pymodbus.exceptions import ConnectionException, ModbusException, ModbusIOException
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
    Setup: TypeAlias = tuple[str | bytes | bytearray, int, int, int, bool]

    def __init__(self, setup: Setup):
        log.info("Creating with: %s" % str(setup))
        self.setup = setup
        super().__init__()

    def clone(self):
        return PySolarmanV5((self.get_host(), self.get_serial(), self.get_port(),
                            self.get_type(), self.get_address()))

    def get_host(self):
        return self.setup[0]

    def get_serial(self):
        return self.setup[1]
    
    def get_port(self):
        return self.setup[2]

    def get_type(self):
        return self.setup[3]
    
    def get_address(self):
        return self.setup[4]

    def get_config_dict(self):
        return {
            "connection": "SOLARMAN",
            "type": self.get_type(),
            "address": self.get_address(),
            "host": self.get_host(),
            "port": self.get_port(),
        }

    def get_config(self):
        return (
            "SOLARMAN",
            self.get_host(),
            self.get_serial(),
            self.get_port(),
            self.get_type(),
            self.get_address(),
        )
    
    def set_host(self, host):
        self.setup = (host, self.get_serial(), self.get_port(), self.get_type(), self.get_address())

    def _create_client(self, **kwargs):
        return PySolarmanV5(self.get_host(), 
                            self.get_serial(), 
                            self.get_port(), 
                            self.get_address(), 
                            False, 
                            **kwargs)

    # Template method
    def _read_registers(self, operation, scan_start, scan_range):
        if operation != 0x04:
            resp = self.client.read_input_registers(self.get_address(), scan_start, scan_range)
        elif operation == 0x03:
            resp = self.client.read_holding_registers(self.get_address(), scan_start, scan_range)
        return resp