from .inverter import Inverter
from pyModbusTCP.client import ModbusClient
from .inverter_types import INVERTERS, READ, HOLDING, SCAN_RANGE, SCAN_START
from typing_extensions import TypeAlias


# create a host tuple alias


class InverterTCP(Inverter):

  Setup: TypeAlias = tuple[str | bytes | bytearray, int, str] # address acceptable for an AF_INET socket with inverter type

  def __init__(self, setup: Setup):
    self.setup = setup
    self.registers = INVERTERS[self.getType()]
    print("InverterTCP: ", self.registers)
    print(self.getType())

  def getHost(self):
    return self.setup[0]
  
  def getPort(self):
    return self.setup[1]
  
  def getType(self):
    return self.setup[2]

  def open(self):
    self.client = ModbusClient(host=self.getHost(), port=self.getPort(), auto_open=False, auto_close=False)
    return self.client.open()

  def close(self):
    self.client.close()

  def read(self):
    regs = []
    vals = []

    for entry in self.registers[READ]:
      scan_start = entry[SCAN_START]
      scan_range = entry[SCAN_RANGE]
      
      print("reading register:", scan_start, "-", scan_range)

      # Populate a list of registers that we want to read from
      r = [x for x in range(
          scan_start, scan_start + scan_range, 1)]

      # Read the registers
      try:
        v = self.client.read_input_registers(
          scan_start, scan_range)
        print("Reading:", scan_start, "-", scan_range, ":", v)
      except: 
        print("error reading register:", scan_start, "-", scan_range)

      regs += r
      vals += v

    # Zip the registers and values together convert them into a dictionary
    res = dict(zip(regs, vals))

    if res:
      return res
    else:
      raise Exception("read error")

  def readPower(self):
    return -1

  def readEnergy(self):
    return -1

  def readFrequency(self):
    return -1
