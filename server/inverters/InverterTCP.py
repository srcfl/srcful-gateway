from .inverter import Inverter
from pymodbus.client import ModbusTcpClient as ModbusClient
from .inverter_types import INVERTERS, OPERATION, SCAN_RANGE, SCAN_START
from typing_extensions import TypeAlias
import logging
import time


logging.basicConfig()
log = logging.getLogger('pymodbus')
log.setLevel(logging.WARNING)

# create a host tuple alias


class InverterTCP(Inverter):

  # address acceptable for an AF_INET socket with inverter type
  Setup: TypeAlias = tuple[str | bytes | bytearray, int, str, int]

  def __init__(self, setup: Setup):
    """
    To-Dos:
    1. Add a check for whether the inverter connection is TCP/IP or RS485 (RTU) and 
    create the client object accordingly
    """
    print("InverterTCP: ", setup)
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
    try:
      v = self.client.read_input_registers(
          scan_start, scan_range, slave=self.getAddress())
      print("OK - Reading Input:", scan_start, "-", scan_range)
    except:
      print("error reading input registers:",
            scan_start, "-", scan_range)
    return v

  def readHoldingRegisters(self, scan_start, scan_range):
    """
    Read a range of holding registers from a start address
    """
    try:
      v = self.client.read_holding_registers(
          scan_start, scan_range, slave=self.getAddress())
      print("OK - Reading Holding:", scan_start, "-", scan_range)
    except:
      print("error reading holding registers:",
            scan_start, "-", scan_range)
    return v

  def readPower(self):
    return -1

  def readEnergy(self):
    return -1

  def readFrequency(self):
    return -1
