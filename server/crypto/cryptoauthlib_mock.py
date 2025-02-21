# mocking the used crypto functions
# this is basically a copy of https://github.com/MicrochipTech/cryptoauthlib/blob/main/python/tests/cryptoauthlib_mock.py
# the purpose is to be able to run the server without the crypto chip

from ctypes import create_string_buffer, memmove, byref, cast, c_void_p
from .status_mock import Status

r_revision = create_string_buffer(4)
r_revision.value = bytes(bytearray([0, 1, 2, 3]))
c_ptr = type(byref(create_string_buffer(1)))

r_signature = create_string_buffer(64)
r_signature.value = bytes(bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                                     0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                                     0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                                     0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]))


r_genkey_pubkey = create_string_buffer(64)
r_genkey_pubkey.value = bytes(bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                                         0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                                         0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                                         0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]))


def atcab_random(random_data):
    return Status.ATCA_SUCCESS


def atcab_init(cfg):
    return Status.ATCA_SUCCESS


def atcab_release():
    return Status.ATCA_SUCCESS


def cfg_ateccx08a_i2c_default():
    # this is just some hard coded mock values

    class Cfg:
        def __init__(self) -> None:
            class CfgAtcai2c:
                def __init__(self) -> None:
                    class Info:
                        def __init__(self) -> None:
                            self.bus = 1
                            self.address = 0x6A
                            self.baud = 400000

                    self.atcai2c = Info()

            self.cfg = CfgAtcai2c()

    return Cfg()


# --------------------------------------------------------------------#
# atcab_info(revision):

# fixed to be more like the original and avoid TypeError as arg is byte array:
# https://github.com/MicrochipTech/cryptoauthlib/blob/79013219556263bd4a3a43678a5e1d0faddba5ba/python/cryptoauthlib/atcab.py#L1323
def atcab_info(revision):

    c_revision = create_string_buffer(4)
    if not isinstance(byref(c_revision), c_ptr):
        raise TypeError

    memmove(cast(c_revision, c_void_p).value, cast(byref(r_revision), c_void_p).value, len(r_revision))
    revision[0:] = bytes(c_revision.raw)

    return Status.ATCA_SUCCESS


def get_device_name(revision):
    """
    Returns the device name based on the info byte array values returned by atcab_info
    """
    devices = {0x10: 'ATECC108A',
               0x50: 'ATECC508A',
               0x60: 'ATECC608',
               0x20:  get_device_name_with_device_id(revision),
               0x00: 'ATSHA204A',
               0x02: 'ATSHA204A',
               0x40: 'ATSHA206A'}
    device_name = devices.get(revision[2], 'UNKNOWN')
    return device_name


def get_device_name_with_device_id(revision):
    """
    Returns the device name based on the info byte array values returned by atcab_info for ECC204 family
    """
    devices = {0x00: 'ECC204',
               0x5A: 'ECC204',
               0x6A: 'TA010',
               0x35: 'SHA104',
               0x3B: 'SHA105'}

    device_name = devices.get(revision[1], 'UNKNOWN')
    return device_name


# --------------------------------------------------------------------#
# atcab_sign(key_id, msg, signature):
def atcab_sign(key_id, msg, signature):

    if not isinstance(key_id, int):
        raise TypeError

    if not isinstance(msg, bytes):
        raise TypeError

    c_signature = create_string_buffer(64)
    if not isinstance(byref(c_signature), c_ptr):
        raise TypeError

    memmove(cast(c_signature, c_void_p).value, cast(byref(r_signature), c_void_p).value, len(r_signature))
    signature[0:] = bytes(c_signature.raw)

    return Status.ATCA_SUCCESS


# --------------------------------------------------------------------#
# atcab_read_serial_number(serial_number):
# modified to be more like the original and require byte array as argument
# https://github.com/MicrochipTech/cryptoauthlib/blob/79013219556263bd4a3a43678a5e1d0faddba5ba/python/cryptoauthlib/atcab.py#L1811
def atcab_read_serial_number(serial_number):
    r_ser_num = create_string_buffer(9)
    r_ser_num.value = bytes(
        bytearray([0xD0, 0x0E, 0x0A, 0x0D, 0x0B, 0x0E, 0x0E, 0x0F, 0x00, 0x00, 0x00])
    )

    c_serial_number = create_string_buffer(9)
    if not isinstance(byref(c_serial_number), c_ptr):
        raise TypeError
    if not isinstance(serial_number, bytearray):
        status = Status.ATCA_BAD_PARAM
    else:
        memmove(
            cast(c_serial_number, c_void_p).value,
            cast(byref(r_ser_num), c_void_p).value,
            len(r_ser_num),
        )
        serial_number[0:] = bytes(c_serial_number.raw)
        status = Status.ATCA_SUCCESS

    return status


# --------------------------------------------------------------------#
# atcab_get_pubkey(key_id, public_key):
def atcab_get_pubkey(key_id, public_key):

    if not isinstance(key_id, int):
        raise TypeError

    c_public_key = create_string_buffer(64)

    if not isinstance(byref(c_public_key), c_ptr):
        raise TypeError

    memmove(
        cast(c_public_key, c_void_p).value,
        cast(byref(r_genkey_pubkey), c_void_p).value,
        len(r_genkey_pubkey),
    )
    public_key[0:] = bytes(c_public_key.raw)

    return Status.ATCA_SUCCESS


# --------------------------------------------------------------------#
# atcab_verify(public_key, signature, data):
def atcab_verify(public_key, signature, data):
    """Mock hardware verification - always returns success in mock implementation.

    In real hardware this would perform actual signature verification.
    """
    return Status.ATCA_SUCCESS
