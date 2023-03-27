from .inverter import Inverter
from pyModbusTCP.client import ModbusClient
from .inverter_types import INVERTERS
from typing_extensions import TypeAlias


# create a host tuple alias


class InverterTCP(Inverter):

  Setup: TypeAlias = tuple[str | bytes | bytearray, int, str] # address acceptable for an AF_INET socket with inverter type

  def __init__(self, setup: Setup):
    self.setup = setup
    self.registers = INVERTERS[self.getType()]

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

    for entry in self.registers["holding"]:

      # Populate a list of registers that we want to read from
      r = [x for x in range(
          entry["scan_start"], entry["scan_start"] + entry["scan_range"], 1)]

      # Read the registers
      v = self.client.read_holding_registers(
          entry["scan_start"], entry["scan_range"])

      regs += r
      vals += v

    # Zip the registers and values together convert them into a dictionary
    res = dict(zip(regs, vals))

    if res:
      return res
    else:
      raise Exception("read error")

  def readPower(self):
    regs = self.client.read_holding_registers(
        40069, 1)  # Hardcoded valye for now
    if regs:
      return regs[0]
    else:
      raise Exception("read error")

  def readEnergy(self):
    regs = self.client.read_holding_registers(
        40069, 1)  # Hardcoded valye for now
    if regs:
      return regs[0]
    else:
      raise Exception("read error")

  def readFrequency(self):
    regs = self.client.read_holding_registers(
        40085, 1)  # Hardcoded valye for now
    if regs:
      return regs[0] * 0.01
    else:
      raise Exception("read error")
