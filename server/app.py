from flask import Flask

import os

from cryptoauthlib import atcab_init, cfg_ateccx08a_i2c_default, atcab_info, get_device_name, atcab_release, atcab_sign, atcab_read_serial_number

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


from pyModbusTCP.client import ModbusClient

app = Flask(__name__)

def initChip():
  cfg = cfg_ateccx08a_i2c_default()
  cfg.cfg.atcai2c.bus = 1 #raspberry pi
  icfg = getattr(cfg.cfg, 'atcai2c')
  setattr(icfg, "address",  int('6a', 16))
  atcab_init(cfg)

@app.route("/")
def hello():
  initChip()

  info = bytearray(4)
  atcab_info(info)
  device_name = get_device_name(info)

  serial_number = bytearray(12)
  atcab_read_serial_number(serial_number)

  atcab_release()

  return 'device: ' + device_name + ' serial: ' + serial_number.hex()

@app.route("/modbus")
def modbus():
  c = ModbusClient(host="127.0.0.1", auto_open=True, auto_close=True)
  regs = c.read_holding_registers(0, 2)

  if regs:
    return str(regs)
  else:
    return "read error"


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(debug=True,host='0.0.0.0',port=port)