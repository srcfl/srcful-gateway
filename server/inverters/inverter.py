import struct
from enum import Enum

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

  def close(self):
    '''Closes the Modbus connection to the inverter.'''
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

  def readHarvestData(self):
    '''Reads the inverter's data.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def populateRegisters(self):
    '''Populates the inverter's registers.'''
    raise NotImplementedError("Subclass must implement abstract method")
 
  def readInputRegisters(self, scan_start, scan_range):
    '''Reads the inverter's input registers.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def readHoldingRegisters(self, scan_start, scan_range):
    '''Reads the inverter's holding registers.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def writeRegisters(self, starting_register, values):
    '''Writes the inverter's registers.'''
    raise NotImplementedError("Subclass must implement abstract method")
  
  
  
  class RegisterEndianness(Enum):
    BIG = 'big'
    LITTLE = 'little'

    @classmethod
    def from_str(cls, string):
      if string == 'big' or string == 'be' or string == '>':
        return cls.BIG
      elif string == 'little' or string == 'le' or string == '<':
        return cls.LITTLE
      else:
        raise Exception("Unsupported endianess " + string)

  class RegisterType(Enum):
    UINT = 'uint'
    INT = 'int'
    FLOAT = 'float'
    ASCII = 'ascii'
    UTF16 = 'utf16'

    @classmethod
    def from_str(cls, string):
      if string == 'uint':
        return cls.UINT
      elif string == 'int':
        return cls.INT
      elif string == 'float':
        return cls.FLOAT
      elif string == 'ascii':
        return cls.ASCII
      elif string == 'utf16':
        return cls.UTF16
      else:
        raise Exception("Unsupported datatype " + string)
  
  @staticmethod
  def formatValue(raw:list, type:RegisterType, endianess: RegisterEndianness):
        
    value = None

    if type == Inverter.RegisterType.UINT:
        value = int.from_bytes(raw, byteorder=endianess.value, signed=False)
    elif type == Inverter.RegisterType.INT:
        value = int.from_bytes(raw, byteorder=endianess.value, signed=True)
    elif type == Inverter.RegisterType.FLOAT:

      if endianess == Inverter.RegisterEndianness.BIG:
          endianess = '>'
      else:
          endianess = '<'

      if len(raw) == 4:
          value = struct.unpack(f'{endianess}f', raw)[0]
      elif len(raw) == 8:
          value = struct.unpack(f'{endianess}d', raw)[0]
      else:
        raise Exception(f"Unsupported float length : {len(raw)}")


    elif type == Inverter.RegisterType.ASCII:
        value = raw.decode('ascii')
    elif type == Inverter.RegisterType.UTF16:
        value = raw.decode('utf-16' + ('be' if endianess.value == 'big' else 'le'))
    else:
      raise Exception("Unsupported datatype " + type.value)
    
    return value