from base64 import urlsafe_b64encode
import json
import base64
import threading

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


ATCA_SUCCESS = 0x00



class Chip:
    _lock = threading.Lock()
    _lock_count = 0

    def __enter__(self):
        """Prepare the chip. Automatically run at the start of `with` block."""
        #if not self.init_chip():
        #    raise RuntimeError("Could not initialize chip!")
        self._init_chip()
        return self  # or return anything you want

    def __exit__(self, type, value, traceback):
        """Clean up the chip. Automatically run at the end of `with` block."""
        self._release()
        #if not self._release():
        #    logging.error("Failed to release chip!")

    def _init_chip(self) -> bool:
        self._lock.acquire()
        self._lock_count += 1

        if self._lock_count != 1:
            self._lock.release()
            old_count = self._lock_count
            self._lock_count = 0
            raise RuntimeError(f"Chip lock count is not 1 after init: {old_count}")

        # this is for raspberry pi should probably be checked better
        cfg = cfg_ateccx08a_i2c_default()
        cfg.cfg.atcai2c.bus = 1  # raspberry pi
        cfg.cfg.atcai2c.address = int("6a", 16)

        if atcab_init(cfg) != ATCA_SUCCESS:
            cfg.cfg.atcai2c.address = int("c0", 16)
            return atcab_init(cfg) == ATCA_SUCCESS
        return True

    def _release(self) -> bool:
        ret = atcab_release()
        self._lock_count -= 1
        self._lock.release()
        if self._lock_count != 0:
            raise RuntimeError(f"Chip lock count is not 0 after release: {self._lock_count}")
        return ret == ATCA_SUCCESS

    def ensure_chip_initialized(self):
        if self._lock_count != 1:
            raise RuntimeError("Chip must be initialized before use!")

    def get_device_name(self):
        self.ensure_chip_initialized()
        info = bytearray(4)
        atcab_info(info)
        return actab_get_device_name(info)

    def get_serial_number(self):
        self.ensure_chip_initialized()
        serial_number = bytearray(12)
        atcab_read_serial_number(serial_number)
        return serial_number

    def public_key_2_pem(self, public_key: bytearray) -> str:
        der = bytearray.fromhex("3059301306072A8648CE3D020106082A8648CE3D03010703420004")
        public_key_b64 = base64.b64encode(der + public_key).decode("ascii")
        return public_key_b64

    def get_public_key(self):
        self.ensure_chip_initialized()
        public_key = bytearray(64)
        atcab_get_pubkey(0, public_key)

        return public_key

    def get_chip_info(self):
        self.ensure_chip_initialized()
        return {
            "deviceName": self.get_device_name(),
            "serialNumber": self.get_serial_number().hex(),
            "publicKey": self.get_public_key().hex(),
        }

    def build_header(self, inverter_model) -> dict:
        self.ensure_chip_initialized()
        return {
            "alg": "ES256",
            "typ": "JWT",
            "device": self.get_serial_number().hex(),
            "opr": "production",
            "model": inverter_model,
        }

    def get_signature(self, data_to_sign):
        self.ensure_chip_initialized()
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(str.encode(data_to_sign))
        message = digest.finalize()

        signature = bytearray(64)
        atcab_sign(0, message, signature)

        return signature

    @staticmethod
    def base64_url_encode(data):
        return urlsafe_b64encode(data).rstrip(b"=")
    
    @staticmethod
    def jwtlify(data):
        return Chip.base64_url_encode(json.dumps(data).encode("utf-8")).decode("utf-8")

    def build_jwt(self, data_2_sign, inverter_model):
        self.ensure_chip_initialized()
        header_base64 =Chip.jwtlify(self.build_header(inverter_model))

        payload_base64 =Chip.jwtlify(data_2_sign)
        header_and_payload = header_base64 + "." + payload_base64

        signature = self.get_signature(header_and_payload)

        signature_base64 = Chip.base64_url_encode(signature).decode("utf-8")

        return header_and_payload + "." + signature_base64
