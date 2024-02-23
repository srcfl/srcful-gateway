from .inverter import Inverter
from pymodbus.client import ModbusTcpClient as ModbusClient

from typing_extensions import TypeAlias
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
# create a host tuple alias


class InverterTCP(Inverter):

    """
    ip: string, IP address of the inverter,
    port: int, Port of the inverter,
    type: string, solaredge, huawei or fronius etc...,
    address: int, Modbus address of the inverter
    """

    Setup: TypeAlias = tuple[str | bytes | bytearray, int, str, int]

    def __init__(self, setup: Setup):
        log.info("Creating with: %s" % str(setup))
        self.setup = setup
        super().__init__()

    def clone(self):
        return InverterTCP((self.get_host(), self.get_port(),
                            self.get_type(), self.get_address()))

    def get_host(self):
        return self.setup[0]

    def get_port(self):
        return self.setup[1]

    def get_type(self):
        return self.setup[2]

    def get_address(self):
        return self.setup[3]

    def get_config_dict(self):
        return {
            "connection": "TCP",
            "type": self.get_type(),
            "address": self.get_address(),
            "host": self.get_host(),
            "port": self.get_port(),
        }

    def get_config(self):
        return (
            "TCP",
            self.get_host(),
            self.get_port(),
            self.get_type(),
            self.get_address(),
        )

    def _create_client(self, **kwargs):
        return ModbusClient(
            host=self.get_host(), port=self.get_port(), unit_id=self.get_address(),
            **kwargs
        )
