import logging
log = logging.getLogger(__name__)

try:
    # https://github.com/MicrochipTech/cryptoauthlib/blob/79013219556263bd4a3a43678a5e1d0faddba5ba/python/cryptoauthlib/atcab.py#L1
    from cryptoauthlib import (
        atcab_init,
        cfg_ateccx08a_i2c_default,
        atcab_info,
        get_device_name as actab_get_device_name,
        atcab_release,
        atcab_sign,
        atcab_read_serial_number,
        atcab_get_pubkey,
    )
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes

except Exception:

    from .cryptoauthlib_mock import (
        atcab_init,
        cfg_ateccx08a_i2c_default,
        atcab_info,
        get_device_name as actab_get_device_name,
        atcab_release,
        atcab_sign,
        atcab_read_serial_number,
        atcab_get_pubkey,
    )
    from .hazmat_mock import default_backend
    from .hazmat_mock import hashes


    log.info("Using mock cryptoauthlib and hazmat")


from base64 import urlsafe_b64encode
import json
import base64
import threading

ATCA_SUCCESS = 0x00

lock = threading.Lock()

def init_chip() -> bool:
    lock.acquire()
    # this is for raspberry pi should probably be checked better
    cfg = cfg_ateccx08a_i2c_default()
    cfg.cfg.atcai2c.bus = 1  # raspberry pi
    cfg.cfg.atcai2c.address = int("6a", 16)

    if atcab_init(cfg) != ATCA_SUCCESS:
        cfg.cfg.atcai2c.address = int("c0", 16)

    return atcab_init(cfg) == ATCA_SUCCESS


def release() -> bool:
    ret = atcab_release()
    lock.release()
    return ret == ATCA_SUCCESS

def get_device_name():
    info = bytearray(4)
    atcab_info(info)
    return actab_get_device_name(info)


def get_serial_number():
    serial_number = bytearray(12)
    atcab_read_serial_number(serial_number)
    return serial_number


def public_key_2_pem(public_key: bytearray) -> str:
    der = bytearray.fromhex("3059301306072A8648CE3D020106082A8648CE3D03010703420004")
    public_key_b64 = base64.b64encode(der + public_key).decode("ascii")
    return public_key_b64


def get_public_key():
    public_key = bytearray(64)
    atcab_get_pubkey(0, public_key)

    return public_key


def get_chip_info():
    return {
        "deviceName": get_device_name(),
        "serialNumber": get_serial_number().hex(),
        "publicKey": get_public_key().hex(),
    }


def build_header(inverter_model) -> dict:
    return {
        "alg": "ES256",
        "typ": "JWT",
        "device": get_serial_number().hex(),
        "opr": "production",
        "model": inverter_model,
    }


def get_signature(data_to_sign):
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(str.encode(data_to_sign))
    message = digest.finalize()

    signature = bytearray(64)
    atcab_sign(0, message, signature)

    return signature


def base64_url_encode(data):
    return urlsafe_b64encode(data).rstrip(b"=")


def build_jwt(data_2_sign, inverter_model):
    header = build_header(inverter_model)

    header_json = json.dumps(header).encode("utf-8")
    header_base64 = base64_url_encode(header_json).decode("utf-8")

    payload_json = json.dumps(data_2_sign).encode("utf-8")
    payload_base64 = base64_url_encode(payload_json).decode("utf-8")

    header_and_payload = header_base64 + "." + payload_base64

    signature = get_signature(header_and_payload)

    signature_base64 = base64_url_encode(signature).decode("utf-8")

    return header_and_payload + "." + signature_base64
