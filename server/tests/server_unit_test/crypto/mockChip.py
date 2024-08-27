from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption
from cryptography.utils import int_to_bytes
import os
import pytest
from unittest.mock import patch
from server.crypto import crypto


def load_env_file(file_path):
    env_vars = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                env_vars[key] = value.strip('"').strip("'")
    return env_vars

def load_private_key_from_hex(private_key_hex):
    private_value = int(private_key_hex, 16)
    pk = ec.derive_private_key(private_value, ec.SECP256R1())

    # check that the private key matches the public key
    expected_public_key = "2f5d41eacf701c18eb1bdae549ee0232ed2b9f3dd2b983ff7b68240bbba84f7b4903d0a52a1ab3d47e7155c5f3455fdbe7997bf85b2258fee6644e16b7e8e9be"
    public_key = pk.public_key()
    public_numbers = public_key.public_numbers()
    public_key_hex = format(public_numbers.x, '064x') + format(public_numbers.y, '064x')
    assert public_key_hex == expected_public_key
    public_key_hex = pk.public_key().public_bytes(encoding=Encoding.X962, format=PublicFormat.UncompressedPoint)[1:].hex()
    assert public_key_hex == expected_public_key
    return pk


def get_test_private_key_serial():
    env_vars = load_env_file('test_config.env')
    private_key_hex = env_vars.get('TEST_PRIVATE_KEY')
    if not private_key_hex:
        raise ValueError("TEST_PRIVATE_KEY variable not set in test_config.env")
    return load_private_key_from_hex(private_key_hex), bytes.fromhex(env_vars.get('TEST_SERIAL'))

class MockCryptoChip:
    def __init__(self):
        

        self.private_key, self.serial_number = get_test_private_key_serial()
        self.public_key = self.private_key.public_key()
        # self.serial_number = b'f42ea576ac87184445'  # You might want to make this configurable too

    def get_public_key(self):
        return self.public_key.public_bytes(
            encoding=Encoding.X962,
            format=PublicFormat.UncompressedPoint
        )[1:]  # Remove the leading byte

    def get_private_key_pem(self):
        return self.private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        ).decode('utf-8')
    
    def get_public_key_pem(self):
        return self.public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def sign(self, message:bytes):
        # The message here is already a digest, so we don't need to hash it again
        signature = self.private_key.sign(
            message,
            ec.ECDSA(utils.Prehashed(hashes.SHA256()))
        )
        (r, s) = utils.decode_dss_signature(signature)
        return int_to_bytes(r, 32) + int_to_bytes(s, 32)



def mock_atcab_sign(key_id, message, signature):
    mock_chip = MockCryptoChip()
    sig = mock_chip.sign(message)
    signature[:] = sig
    return 0  # ATCA_SUCCESS

_mocked_chip = MockCryptoChip()

@pytest.fixture
def mock_crypto_chip():
    return _mocked_chip


@pytest.fixture
def patched_chip(mock_crypto_chip):
    with patch('server.crypto.crypto.atcab_init') as mock_init, \
         patch('server.crypto.crypto.atcab_read_serial_number') as mock_read_serial, \
         patch('server.crypto.crypto.atcab_get_pubkey') as mock_get_pubkey, \
         patch('server.crypto.crypto.atcab_sign', side_effect=mock_atcab_sign):
        
        mock_init.return_value = 0

        def read_serial_side_effect(serial):
            serial[:] = mock_crypto_chip.serial_number
            return 0

        mock_read_serial.side_effect = read_serial_side_effect

        def get_pubkey_side_effect(key_id, public_key):
            public_key[:] = mock_crypto_chip.get_public_key()
            return 0

        mock_get_pubkey.side_effect = get_pubkey_side_effect

        yield crypto.Chip()