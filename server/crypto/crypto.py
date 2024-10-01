from base64 import urlsafe_b64encode
import json
import base64
from base58 import b58encode_check
import threading
from .crypto_interface import CryptoInterface
from .software import SoftwareCrypto

import logging
log = logging.getLogger(__name__)

try:
    # https://github.com/MicrochipTech/cryptoauthlib/blob/79013219556263bd4a3a43678a5e1d0faddba5ba/python/cryptoauthlib/atcab.py#L1
    from cryptoauthlib import (
        atcab_init,
        cfg_ateccx08a_i2c_default,
        atcab_info,
        get_device_name as atcab_get_device_name,
        atcab_release,
        atcab_sign,
        atcab_read_serial_number,
        atcab_get_pubkey,
        atcab_random
    )
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes

except Exception:

    from .cryptoauthlib_mock import (
        atcab_init,
        cfg_ateccx08a_i2c_default,
        atcab_info,
        get_device_name as atcab_get_device_name,
        atcab_release,
        atcab_sign,
        atcab_read_serial_number,
        atcab_get_pubkey,
        atcab_random
    )
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes

    log.info("Using mock cryptoauthlib and hazmat")


ATCA_SUCCESS = 0x00




class HardwareCrypto(CryptoInterface):
    def __init__(self):
        from cryptoauthlib import atcab_init, atcab_release, atcab_info, atcab_read_serial_number, atcab_get_pubkey, atcab_sign
        self._atcab_init = atcab_init
        self._atcab_release = atcab_release
        self._atcab_info = atcab_info
        self._atcab_read_serial_number = atcab_read_serial_number
        self._atcab_get_pubkey = atcab_get_pubkey
        self._atcab_sign = atcab_sign
        self._atcab_random = atcab_random
    def atcab_init(self, cfg):
        return self._atcab_init(cfg)

    def atcab_release(self):
        return self._atcab_release()

    def atcab_info(self):
        revision = bytearray(4)
        status = self._atcab_info(revision)
        return status, bytes(revision)

    def atcab_read_serial_number(self):
        serial_number = bytearray(12)
        status = self._atcab_read_serial_number(serial_number)
        return status, bytes(serial_number)

    def atcab_get_pubkey(self, key_id):
        public_key = bytearray(64)
        status = self._atcab_get_pubkey(key_id, public_key)
        return status, bytes(public_key)

    def atcab_sign(self, key_id, message):
        signature = bytearray(64)
        status = self._atcab_sign(key_id, message, signature)
        return status, bytes(signature)
    
    def atcab_random(self):
        random_bytes = bytearray(32)
        status = self._atcab_random(random_bytes)
        return status, bytes(random_bytes)

def base64_url_encode(data):
    return urlsafe_b64encode(data).rstrip(b"=")

def jwtlify(data:dict) -> bytes:
    return base64_url_encode(json.dumps(data).encode("utf-8")).decode("utf-8")

def public_key_to_compact(pub_key:bytearray) -> bytes:
    assert len(pub_key) == 64
    x_as_bytes = pub_key[:32]
    x_as_b58_encoded = b58encode_check(bytes([0, 0]) + x_as_bytes) # helium adds 0, 0 and not the real high/low bit

    return x_as_b58_encoded



class Chip:
    _lock = threading.Lock()
    _lock_count = 0

    
    def __init__(self, crypto_impl: CryptoInterface = SoftwareCrypto()):
    # def __init__(self, crypto_impl: CryptoInterface = HardwareCrypto()):
        self.crypto_impl = crypto_impl

    class Error(Exception):
        def __init__(self, code, message):
            self.code = code
            self.message = message
            super().__init__(self.message)

        def __str__(self) -> str:
            return super().__str__() + f" cryptauthlib error code: {self.code}"

    def __enter__(self):
        """Prepare the chip. Automatically run at the start of `with` block."""
        # if not self.init_chip():
        #    raise RuntimeError("Could not initialize chip!")
        try:
            self._init_chip()
        except Exception as e:
            self._lock.release()
            raise e
        return self  # or return anything you want

    def __exit__(self, type, value, traceback):
        """Clean up the chip. Automatically run at the end of `with` block."""
        self._release()
        # if not self._release():
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
        cfg.cfg.atcai2c.address = 0x6a

        if self.crypto_impl.atcab_init(cfg) != ATCA_SUCCESS:
            cfg.cfg.atcai2c.address = 0xc0
            self._throw_on_error(self.crypto_impl.atcab_init(cfg), "Failed to initialize chip.")
        return True
    
    def _throw_on_error(self, code: int, message: str):
        if code != ATCA_SUCCESS:
            # we do not want to release as there may caught exceptions
            # self._lock.release()
            raise Chip.Error(code, message)

    def _release(self) -> bool:
        ret = self.crypto_impl.atcab_release()
        self._lock_count -= 1
        self._lock.release()
        if self._lock_count != 0:
            raise RuntimeError(f"Chip lock count is not 0 after release: {self._lock_count}")
        return ret == ATCA_SUCCESS

    def ensure_chip_initialized(self):
        if self._lock_count != 1:
            raise RuntimeError("Chip must be initialized before use!")
        
    def get_random(self):
        self.ensure_chip_initialized()
        code, random_bytes = self.crypto_impl.atcab_random()
        self._throw_on_error(code, "Failed to get random bytes")
        return random_bytes

    def get_device_name(self):
        self.ensure_chip_initialized()
        code, info = self.crypto_impl.atcab_info()
        return atcab_get_device_name(info)  # this one does not access the hardware chiop at all so we do not need to inject it, but it could be nice to do in the future

    def get_serial_number(self, retries:int=0) -> bytearray:
        self.ensure_chip_initialized()
        code, ret = self.crypto_impl.atcab_read_serial_number()
        if retries > 0 and code != ATCA_SUCCESS:
            
            return self.get_serial_number(retries - 1)
            
        self._throw_on_error(code, "Failed to read serial number")
        return ret

    def public_key_2_pem(self, public_key: bytearray) -> str:
        der = bytearray.fromhex("3059301306072A8648CE3D020106082A8648CE3D03010703420004")
        public_key_b64 = base64.b64encode(der + public_key).decode("ascii")
        return public_key_b64

    def get_public_key(self, retries:int=0) -> bytearray:
        self.ensure_chip_initialized()

        code, public_key = self.crypto_impl.atcab_get_pubkey(0)
        if retries > 0 and code != ATCA_SUCCESS:
            return self.get_public_key(retries - 1)

        self._throw_on_error(code, "Failed to get public key")

        return public_key

    # def get_chip_info(self):
    #     self.ensure_chip_initialized()
    #     return {
    #         "deviceName": self.get_device_name(),
    #         "serialNumber": self.get_serial_number().hex(),
    #         "publicKey": self.get_public_key().hex(),
    #     }

    def build_header(self, headers:dict) -> dict:
        self.ensure_chip_initialized()
        header_dict = {
            "alg": "ES256",
            "typ": "JWT",
            "device": self.get_serial_number().hex(),
            "opr": "production"
        }
        
        for header_key in headers:
            header_dict[header_key] = headers[header_key]

        return header_dict

    def get_signature(self, data_to_sign, retries:int = 0) -> bytearray:
        self.ensure_chip_initialized()
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(str.encode(data_to_sign))
        message = digest.finalize()

        code, signature = self.crypto_impl.atcab_sign(0, message)
        if retries > 0 and code != ATCA_SUCCESS:
            return self.get_signature(data_to_sign, retries - 1)
        
        self._throw_on_error(code, "Failed to sign message")
        return signature

    def build_jwt(self, data_2_sign, headers:dict, retries:int=0):
        self.ensure_chip_initialized()
        header_base64 = jwtlify(self.build_header(headers))

        payload_base64 = jwtlify(data_2_sign)
        header_and_payload = header_base64 + "." + payload_base64

        signature = self.get_signature(header_and_payload, retries)

        signature_base64 = base64_url_encode(signature).decode("utf-8")

        return header_and_payload + "." + signature_base64
