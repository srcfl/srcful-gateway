from .inverter import Inverter
from pymodbus.client import ModbusSerialClient as ModbusClient
from typing_extensions import TypeAlias
import logging

log = logging.getLogger(__name__)


class InverterRTU(Inverter):

    """
    port: string, Serial port used for communication,
    baudrate: int, Bits per second,
    bytesize: int, Number of bits per byte 7-8,
    parity: string, 'E'ven, 'O'dd or 'N'one,
    stopbits: float, Number of stop bits 1, 1.5, 2,
    type: string, solaredge, huawei or fronius etc...,
    address: int, Modbus address of the inverter,
    """

    Setup: TypeAlias = tuple[str, int, int, str, float, str, int]

    def __init__(self, setup: Setup):
        log.info("Creating with: %s" % str(setup))
        self.setup = setup
        super().__init__()

    def clone(self):
        return InverterRTU((self.get_host(), self.get_baudrate(),
                            self.get_bytesize(), self.get_parity(),
                            self.get_stopbits(), self.get_type(), self.get_address()))

    def get_host(self):
        return self.setup[0]

    def get_baudrate(self):
        return int(self.setup[1])

    def get_bytesize(self):
        return self.setup[2]

    def get_parity(self):
        return self.setup[3]

    def get_stopbits(self):
        return self.setup[4]

    def get_type(self):
        return self.setup[5]

    def get_address(self):
        return self.setup[6]

    def get_config_dict(self):
        return {
            "connection": "RTU",
            "type": self.get_type(),
            "address": self.get_address(),
            "host": self.get_host(),
            "baudrate": self.get_baudrate(),
            "bytesize": self.get_bytesize(),
            "parity": self.get_parity(),
            "stopbits": self.get_stopbits(),
        }

    def get_config(self):
        return (
            "RTU",
            self.get_host(),
            self.get_baudrate(),
            self.get_bytesize(),
            self.get_parity(),
            self.get_stopbits(),
            self.get_type(),
            self.get_address(),
        )

    def _create_client(self, **kwargs):
        return ModbusClient(
            method="rtu",
            port=self.get_host(),
            baudrate=self.get_baudrate(),
            bytesize=self.get_bytesize(),
            parity=self.get_parity(),
            stopbits=self.get_stopbits(),
            **kwargs
        )
