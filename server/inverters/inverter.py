from enum import Enum
from .inverter_types import OPERATION, SCAN_RANGE, SCAN_START
import logging
from pymodbus.pdu import ExceptionResponse

log = logging.getLogger(__name__)

class Inverter:
  '''Base class for all inverters.'''

  def __init__(self):
    self._isTerminated = False
    pass

  def terminate(self):
    '''Terminates the inverter.'''
    self.close()
    self._isTerminated = True

  def isTerminated(self) -> bool:
    return self._isTerminated
  
  def getConfig(self):
    '''Returns the inverter's setup as a tuple.'''
    raise NotImplementedError("Subclass must implement abstract method")
  
  def getConfigDict(self):
    '''Returns the inverter's setup as a dictionary.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def open(self) -> bool:
    '''Opens the Modbus connection to the inverter.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def getHost(self):
    '''Returns the inverter's host IP-address'''
    raise NotImplementedError("Subclass must implement abstract method")

  def getPort(self):
    '''Returns the inverter's port number'''
    raise NotImplementedError("Subclass must implement abstract method")

  def getType(self):
    '''Returns the inverter's type'''
    raise NotImplementedError("Subclass must implement abstract method")

  def getAddress(self):
    '''Returns the inverter's address'''
    raise NotImplementedError("Subclass must implement abstract method")

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
      vals += v

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
    return [x for x in range(scan_start, scan_start + scan_range, 1)]

  def readInputRegisters(self, scan_start, scan_range):
    """
    Read a range of input registers from a start address
    """
    slave = self.getAddress()
    resp = self.client.read_input_registers(scan_start, scan_range, slave=slave)
    log.debug("OK - Reading Input: " + str(scan_start) + "-" + str(scan_range))
    if isinstance(resp, ExceptionResponse):
      raise Exception("readInputRegisters() - ExceptionResponse: " + str(resp))
    return resp.registers

  def readHoldingRegisters(self, scan_start, scan_range):
    """
    Read a range of holding registers from a start address
    """
    resp = self.client.read_holding_registers(scan_start, scan_range, slave=self.getAddress())
    log.debug("OK - Reading Holding: " + str(scan_start) + "-" + str(scan_range))
    if isinstance(resp, ExceptionResponse):
      raise Exception("readHoldingRegisters() - ExceptionResponse: " + str(resp))
    return resp.registers
  
  def writeRegisters(self, starting_register, values):
    """
    Write a range of holding registers from a start address
    """
    resp = self.client.write_registers(starting_register, values, slave=self.getAddress())
    log.debug("OK - Writing Holdings: " + str(starting_register) + "-" + str(values))
    if isinstance(resp, ExceptionResponse):
      raise Exception("writeRegisters() - ExceptionResponse: " + str(resp))
    return resp
  