from .inverter import Inverter
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.pdu import ExceptionResponse
from .inverter_types import INVERTERS
from typing_extensions import TypeAlias
import logging
import time

log = logging.getLogger(__name__)

# set logging info for pymodbus to INFO to avoid spamming
from pymodbus import pymodbus_apply_logging_config
pymodbus_apply_logging_config('INFO')

# create a host tuple alias


class InverterTCP(Inverter):

  """
    ip: string, IP address of the inverter,
    port: int, Port of the inverter,
    type: string, solaredge, huawei or fronius etc...,
    address: int, Modbus address of the inverter,
  """
  Setup: TypeAlias = tuple[str | bytes | bytearray, int, str, int]

  def __init__(self, setup: Setup):
    super().__init__()
    log.info("Creating with: %s" % str(setup))
    self.setup = setup
    self.registers = INVERTERS[self.getType()]
    self.inverterIsOpen = False

  def getHost(self):
    return self.setup[0]

  def getPort(self):
    return self.setup[1]

  def getType(self):
    return self.setup[2]

  def getAddress(self):
    return self.setup[3]
  
  def getConfigDict(self):
    return {"connection": "TCP", "type": self.getType(), "address": self.getAddress(), "host": self.getHost(), "port": self.getPort()}

  def getConfig(self):
    return ("TCP", self.getHost(), self.getPort(), self.getType(), self.getAddress())

  def isOpen(self):
    return self.inverterIsOpen

  def open(self):
    if not self.isTerminated():
      self.client = ModbusClient(host=self.getHost(), port=self.getPort(), unit_id=self.getAddress())
      if self.client.connect():
        self.inverterIsOpen = True
        return self.inverterIsOpen
      else:
        self.terminate()
        self.inverterIsOpen = False
        return self.inverterIsOpen
    else:
      return False

 