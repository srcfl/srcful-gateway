from .inverter import Inverter
from pyModbusTCP.client import ModbusClient


class SunspecTCP(Inverter):
  def __init__(self, host):
    self.host = host
    self.client = ModbusClient(host=self.host, auto_open=True, auto_close=True)

  def read(self):
    regs = self.client.read_holding_registers(40069, 20)
    if regs:
        return regs
    else:
        raise Exception("read error")
    
  def readPower(self):
    regs = self.client.read_holding_registers(40069, 20)
    if regs:
        return regs[0]
    else:
        raise Exception("read error")
    
  def readEnergy(self):
    regs = self.client.read_holding_registers(40069, 20)
    if regs:
        return regs[1]
    else:
        raise Exception("read error")
  
  def readFrequency(self):
    regs = self.client.read_holding_registers(40069, 20)
    if regs:
        return regs[2]
    else:
        raise Exception("read error")
