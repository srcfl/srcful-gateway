try:
  # https://github.com/MicrochipTech/cryptoauthlib/blob/79013219556263bd4a3a43678a5e1d0faddba5ba/python/cryptoauthlib/atcab.py#L1
  from cryptoauthlib import atcab_init, cfg_ateccx08a_i2c_default, atcab_info, get_device_name, atcab_release, atcab_sign, atcab_read_serial_number, atcab_get_pubkey
  from cryptography.hazmat.backends import default_backend
  from cryptography.hazmat.primitives import hashes

except:
  from .cryptoauthlib_mock import atcab_init, cfg_ateccx08a_i2c_default, atcab_info, get_device_name, atcab_release, atcab_sign, atcab_read_serial_number, atcab_get_pubkey
  from .hazmat_mock import default_backend
  from .hazmat_mock import hashes
  

from base64 import urlsafe_b64encode, urlsafe_b64decode
import json
import base64

ATCA_SUCCESS = 0x00

def initChip() -> bool:

  # this is for raspberry pi should probably be checked better
  cfg = cfg_ateccx08a_i2c_default()
  cfg.cfg.atcai2c.bus = 1  # raspberry pi
  icfg = getattr(cfg.cfg, 'atcai2c')
  setattr(icfg, "address",  int('6a', 16))

    
  return atcab_init(cfg) == ATCA_SUCCESS


def release() -> bool:
  return atcab_release() == ATCA_SUCCESS


def getDeviceName():
  info = bytearray(4)
  atcab_info(info)
  return get_device_name(info)


def getSerialNumber():
  serial_number = bytearray(12)
  atcab_read_serial_number(serial_number)
  return serial_number

def publicKeyToPEM(public_key: bytearray)->str:
  der = bytearray.fromhex('3059301306072A8648CE3D020106082A8648CE3D03010703420004')
  public_key_b64 = base64.b64encode(der + public_key).decode('ascii')
  return public_key_b64

def getPublicKey():
  public_key = bytearray(64)
  atcab_get_pubkey(0, public_key)

 

  return public_key


def getChipInfo():
  return {'deviceName': getDeviceName(), 'serialNumber': getSerialNumber().hex(), 'publicKey': getPublicKey().hex()}


def buildHeader() -> dict:
  return {
      "alg": "ES256",
      "typ": "JWT",
      "opr": "production",
      "device": getSerialNumber().hex()
  }


def getSignature(dataToSign):
  digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
  digest.update(str.encode(dataToSign))
  message = digest.finalize()

  signature = bytearray(64)
  atcab_sign(0, message, signature)

  return signature


def base64UrlEncode(data):
  return urlsafe_b64encode(data).rstrip(b'=')


def buildJWT(dataToSign):
  header = buildHeader()

  header_json = json.dumps(header).encode('utf-8')
  header_base64 = base64UrlEncode(header_json).decode('utf-8')

  payload_json = json.dumps(dataToSign).encode('utf-8')
  payload_base64 = base64UrlEncode(payload_json).decode('utf-8')

  header_and_payload = header_base64 + "." + payload_base64

  signature = getSignature(header_and_payload)

  signature_base64 = base64UrlEncode(signature).decode('utf-8')

  return header_and_payload + "." + signature_base64
