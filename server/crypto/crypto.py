
try:
  from cryptoauthlib import atcab_init, cfg_ateccx08a_i2c_default, atcab_info, get_device_name, atcab_release, atcab_sign, atcab_read_serial_number
  from cryptography.hazmat.backends import default_backend
  from cryptography.hazmat.primitives import hashes
except:
  from .cryptoauthlib_mock import atcab_init, cfg_ateccx08a_i2c_default, atcab_info, get_device_name, atcab_release, atcab_sign, atcab_read_serial_number

def initChip():
  cfg = cfg_ateccx08a_i2c_default()
  cfg.cfg.atcai2c.bus = 1 #raspberry pi
  icfg = getattr(cfg.cfg, 'atcai2c')
  setattr(icfg, "address",  int('6a', 16))
  atcab_init(cfg)

def release():
  atcab_release()

def getDeviceName():
  info = bytearray(4)
  atcab_info(info)
  return get_device_name(info)
  
def getSerialNumber():
  serial_number = bytearray(12)
  atcab_read_serial_number(serial_number)
  return serial_number.hex()
  
def getChipInfo(self):
  return {'deviceName':self.getDeviceName(), 'serialNumber':self.getSerialNumber()}

def getSignature(self, dataToSign):
  digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
  digest.update(str.encode(dataToSign))
  message = digest.finalize()

  signature = bytearray(64)
  atcab_sign(0, message, signature)

  return signature.hex()
