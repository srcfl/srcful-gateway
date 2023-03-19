from pymodbus.client.sync import ModbusTcpClient as ModbusClient 
def readfrommodbus():
  
  c = ModbusClient(host="127.0.0.1", auto_open=True, auto_close=True)
  regs = c.read_holding_registers(0, 2)

  if regs:
    return str(regs)
  else:
    return "read error"