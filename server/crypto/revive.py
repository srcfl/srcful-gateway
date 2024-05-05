# This seems to revive the crypto chip if it starts to fail with a a 0 pubkey
# this likely needs to be run in a separate process and is NOT a part of the main server

import logging
import time
import sys

from cryptoauthlib import (
    atcab_init,
    cfg_ateccx08a_i2c_default,
    atcab_info,
    # atcab_get_device_name,
    atcab_release,
    # atcab_sign,
    # atcab_read_serial_number,
    atcab_get_pubkey,
    )


logger = logging.getLogger(__name__)


def sleep():
    """sleep for a while"""
    time.sleep(3.1415)


def get_pubkey():
    """get the public key"""
    public_key = bytearray(64)
    code = atcab_get_pubkey(0, public_key)
    msg = f"atcab_get_pubkey: {code} {public_key.hex()}"
    logger.debug(msg)
    print(msg)
    return code


def get_info():
    """get the device info"""
    info = bytearray(4)
    code = atcab_info(info)
    msg = f"atcab_info: {code} {info.hex()}"
    logger.debug(msg)
    print(msg)
    return code


def poke():
    """poke the chip to make it work log the pubkey and info"""
    sleep()
    get_pubkey()
    sleep()
    get_info()
    sleep()
    return get_pubkey()


def init_chip(address: int):
    """initialize the chip with the given address, returns 0 on success"""
    cfg = cfg_ateccx08a_i2c_default()
    cfg.cfg.atcai2c.bus = 1  # raspberry pi
    cfg.cfg.atcai2c.address = address

    return atcab_init(cfg)


def run():
    ret = 1

    # we test type B chip first
    if init_chip(0x6a) == 0:
        ret = poke()
        atcab_release()

    sleep()
    if init_chip(0xc0) == 0:
        ret = poke()
        atcab_release()

    return ret


if __name__ == "__main__":
    ret = run()
    print(f"final return value (0 == success): {ret}")
    sys.exit(ret)
