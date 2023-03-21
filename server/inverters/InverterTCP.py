from .inverter import Inverter
from pyModbusTCP.client import ModbusClient
from .inverter_types import INVERTERS


class InverterTCP(Inverter):
  def __init__(self, host, type):
    self.host = host
    self.registers = INVERTERS[type]

  def open(self):
    self.client = ModbusClient(host=self.host)
    self.client.open()

  def close(self):
    self.client.close()

  def read(self):
    regs = []
    for entry in self.registers["holding"]:
      regs += self.client.read_holding_registers(
          entry["scan_start"], entry["scan_range"])
    if regs:
      return regs
    else:
      raise Exception("read error")

  def readPower(self):
    regs = self.client.read_holding_registers(40069, 1)
    if regs:
      return regs[0]
    else:
      raise Exception("read error")

  def readEnergy(self):
    regs = self.client.read_holding_registers(40069, 1)
    if regs:
      return regs[0]
    else:
      raise Exception("read error")

  def readFrequency(self):
    regs = self.client.read_holding_registers(40085, 1)
    if regs:
      return regs[0] * 0.01
    else:
      raise Exception("read error")
