from .inverter import Inverter
from pymodbus.client import ModbusSerialClient as ModbusClient
from .inverter_types import INVERTERS, OPERATION, SCAN_RANGE, SCAN_START
from typing_extensions import TypeAlias
from pymodbus.pdu import ExceptionResponse
import logging
import time # Why?

log = logging.getLogger(__name__)

# set logging info for pymodbus to INFO to avoid spamming
from pymodbus import pymodbus_apply_logging_config
pymodbus_apply_logging_config('INFO')

# create a host tuple alias


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
    super().__init__()
    log.info("Creating with: %s" % str(setup))
    self.setup = setup
    self.registers = INVERTERS[self.getType()]

  def getHost(self):
    return self.setup[0]
  
  def getBaudrate(self):
    return int(self.setup[1])
  
  def getBytesize(self):
    return self.setup[2]
  
  def getParity(self):
    return self.setup[3]
  
  def getStopbits(self):
    return self.setup[4]
  
  def getType(self):
    return self.setup[5]
  
  def getAddress(self):
    return self.setup[6]
  
  def getConfig(self):
    return ("RTU", self.getHost(), self.getBaudrate(), self.getBytesize(), self.getParity(), self.getStopbits(), self.getType(), self.getAddress())

  def open(self):
    if not self.isTerminated():
      log.info("Opening RTU inverter with config: %s" % str(self.getConfig()))
      self.client = ModbusClient(method='rtu', 
                                 port=self.getHost(), 
                                 baudrate=self.getBaudrate(), 
                                 bytesize=self.getBytesize(), 
                                 parity=self.getParity(), 
                                 stopbits=self.getStopbits(), 
                                 timeout=.1)
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
    v = self.client.read_input_registers(address=scan_start, count=scan_range, slave=self.getAddress())
    log.debug("OK - Reading Input: " + str(scan_start) + "-" + str(scan_range))
    if isinstance(v, ExceptionResponse):
      raise Exception("readInputRegisters() - ExceptionResponse: " + str(v))
    return v

  def readHoldingRegisters(self, scan_start, scan_range):
    """
    Read a range of holding registers from a start address
    """
    v = self.client.read_holding_registers(address=scan_start, count=scan_range, slave=self.getAddress())
    log.debug("OK - Reading Holding: " + str(scan_start) + "-" + str(scan_range))
    if isinstance(v, ExceptionResponse):
      raise Exception("readHoldingRegisters() - ExceptionResponse: " + str(v))

    return v