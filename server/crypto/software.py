from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.utils import int_to_bytes
from cryptography.hazmat.primitives import hashes
from .crypto_interface import CryptoInterface
import random
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def load_env_file(file_path):
    env_vars = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                env_vars[key] = value.strip('"').strip("'")
    return env_vars

def load_env_vars():
    # load from file if exists, otherwise load from environment variables
    env_vars = load_env_file('test_config.env')
    if not env_vars:
        env_vars = os.environ
    return env_vars


def load_private_key_from_hex(private_key_hex):
    private_value = int(private_key_hex, 16)
    pk = ec.derive_private_key(private_value, ec.SECP256R1())

    # check that the private key matches the public key
    # Fetch the expected public key from the environment variable
    env_vars = load_env_vars()
    expected_public_key = env_vars.get('TEST_PUBLIC_KEY')
    if not expected_public_key:
        raise ValueError("TEST_PUBLIC_KEY variable not set in test_config.env")
    public_key = pk.public_key()
    public_numbers = public_key.public_numbers()
    public_key_hex = format(public_numbers.x, '064x') + format(public_numbers.y, '064x')
    assert public_key_hex == expected_public_key
    public_key_hex = pk.public_key().public_bytes(encoding=Encoding.X962, format=PublicFormat.UncompressedPoint)[1:].hex()
    assert public_key_hex == expected_public_key
    return pk


def get_test_private_key_serial():
    env_vars = load_env_vars()
    if "TEST_SERIAL" in env_vars and "TEST_PRIVATE_KEY" in env_vars:
        logger.info("Using test private key and serial number")
        return load_private_key_from_hex(env_vars.get('TEST_PRIVATE_KEY')), bytes.fromhex(env_vars.get('TEST_SERIAL'))
    else:
        logger.error("TEST_SERIAL or TEST_PRIVATE_KEY variable not set in test_config.env")
        raise ValueError("TEST_SERIAL or TEST_PRIVATE_KEY variable not set in test_config.env")


class SoftwareCrypto(CryptoInterface):
    def __init__(self):
        self.private_key, self.serial_number = get_test_private_key_serial()
        self.public_key = self.private_key.public_key()

    def atcab_init(self, cfg):
        return 0    # ATCA_SUCCESS

    def atcab_release(self):
        return 0  # ATCA_SUCCESS

    def atcab_info(self):
        return 0, bytes([0xff, 0xff, 0xff, 0xff])

    def atcab_read_serial_number(self):
        return 0, self.serial_number

    def atcab_get_pubkey(self, key_id):
        public_key = self.public_key.public_bytes(encoding=Encoding.X962, format=PublicFormat.UncompressedPoint)[1:]
        return 0, bytes(public_key)

    def atcab_sign(self, key_id, message):
        signature = self.private_key.sign(
            message,
            ec.ECDSA(utils.Prehashed(hashes.SHA256()))
        )
        (r, s) = utils.decode_dss_signature(signature)
        result = int_to_bytes(r, 32) + int_to_bytes(s, 32)
        return 0, bytes(result)

    def atcab_random(self):
        # generate a list of 32 random bytes
        random_data = [random.randint(0, 255) for _ in range(32)]
        return 0, bytearray(random_data)
