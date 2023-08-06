from .inverter import Inverter
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.pdu import ExceptionResponse
from .inverter_types import INVERTERS, OPERATION, SCAN_RANGE, SCAN_START
from typing_extensions import TypeAlias
import logging
import time

log = logging.getLogger(__name__)

# set logging info for pymodbus to INFO to avoid spamming
from pymodbus import pymodbus_apply_logging_config
pymodbus_apply_logging_config('INFO')

# create a host tuple alias


class InverterTCP(Inverter):

  # address acceptable for an AF_INET socket with inverter type
  Setup: TypeAlias = tuple[str | bytes | bytearray, int, str, int]

  def __init__(self, setup: Setup):
    super().__init__()
    log.info("Creating with: %s" % str(setup))
    self.setup = setup
    self.registers = INVERTERS[self.getType()]

  def getHost(self):
    return self.setup[0]

  def getPort(self):
    return self.setup[1]

  def getType(self):
    return self.setup[2]

  def getAddress(self):
    return self.setup[3]

  def open(self):
    if not self.isTerminated():
      self.client = ModbusClient(host=self.getHost(), port=self.getPort(), unit_id=self.getAddress())
      if self.client.connect():
        return True
      else:
        self.terminate()
        return False
    else:
      return False

  def close(self):
    self.client.close()

  def readHarvestData(self):
    if self.isTerminated():
      raise Exception("readHarvestData() - inverter is terminated")
    regs = []
    vals = []

    for entry in self.registers:

      operation = entry[OPERATION]
      scan_start = entry[SCAN_START]
      scan_range = entry[SCAN_RANGE]

      r = self.populateRegisters(scan_start, scan_range)

      if operation == 0x03:
        v = self.readHoldingRegisters(scan_start, scan_range)
      elif operation == 0x04:
        v = self.readInputRegisters(scan_start, scan_range)
      regs += r
      vals += v.registers

    # Zip the registers and values together convert them into a dictionary
    res = dict(zip(regs, vals))
    if res:
      return res
    else:
      raise Exception("readHarvestData() - res is empty")

  def populateRegisters(self, scan_start, scan_range):
    """
    Populate a list of registers from a start address and a range
    """
    return [x for x in range(
        scan_start, scan_start + scan_range, 1)]

  def readInputRegisters(self, scan_start, scan_range):
    """
    Read a range of input registers from a start address
    """
    v = self.client.read_input_registers(scan_start, scan_range, slave=self.getAddress())
    log.debug("OK - Reading Holding: " + str(scan_start) + "-" + str(scan_range))
    if isinstance(v, ExceptionResponse):
      raise Exception("readInputRegisters() - ExceptionResponse: " + str(v))
    return v

  def readHoldingRegisters(self, scan_start, scan_range):
    """
    Read a range of holding registers from a start address
    """
    #try:
    v = self.client.read_holding_registers(
        scan_start, scan_range, slave=self.getAddress())
    log.debug("OK - Reading Holding: " + str(scan_start) + "-" + str(scan_range))
    # check if v is a ModbusResponse object
    if isinstance(v, ExceptionResponse):
      raise Exception("readHoldingRegisters() - ExceptionResponse: " + str(v))

    return v

  def readPower(self):
    return -1

  def readEnergy(self):
    return -1

  def readFrequency(self):
    return -1
