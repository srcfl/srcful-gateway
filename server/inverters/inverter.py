
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
 
  def readInputRegisters(self):
    '''Reads the inverter's input registers.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def readHoldingRegisters(self):
    '''Reads the inverter's holding registers.'''
    raise NotImplementedError("Subclass must implement abstract method")

  def writeRegisters(self, starting_register, values):
    '''Writes the inverter's registers.'''
    raise NotImplementedError("Subclass must implement abstract method")