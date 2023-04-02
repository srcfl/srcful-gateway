class Inverter:
  '''Base class for all inverters.'''

  def __init__(self):
    pass

  def open(self) -> bool:
    '''Opens the Modbus connection to the inverter.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def close(self):
    '''Closes the Modbus connection to the inverter.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def readHarvestData(self):
    '''Reads the inverter's data.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def populateRegisters(self):
    '''Populates the inverter's registers.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def readInputRegisters(self):
    '''Reads the inverter's input registers.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def readHoldingRegisters(self):
    '''Reads the inverter's holding registers.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def readPower(self):
    '''Reads the inverter's power data.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def readEnergy(self):
    '''Reads the inverter's energy data.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def readFrequency(self):
    '''Reads the inverter's frequency data.'''
    raise NotImplementedError("Subclass must implement abstract method")
