from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.utils import int_to_bytes
from cryptography.hazmat.primitives import hashes
from .crypto_interface import CryptoInterface
import random
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


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
    # Fetch the expected public key from the environment variable
    env_vars = load_env_file('test_config.env')
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
    env_vars = load_env_file('test_config.env')
    private_key_hex = env_vars.get('TEST_PRIVATE_KEY')
    if not private_key_hex:
        raise ValueError("TEST_PRIVATE_KEY variable not set in test_config.env")
    return load_private_key_from_hex(private_key_hex), bytes.fromhex(env_vars.get('TEST_SERIAL'))


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
        """Sign a message using ECDSA with SHA256.

        Args:
            key_id: Key slot to use (ignored in software implementation)
            message: The message to sign (should be SHA256 hash)

        Returns:
            tuple: (status, signature) where signature is in r|s format (64 bytes)
        """
        # Sign the pre-computed hash
        signature = self.private_key.sign(
            message,  # message is already a hash
            ec.ECDSA(utils.Prehashed(hashes.SHA256()))
        )

        # Convert to r|s format (64 bytes)
        r, s = utils.decode_dss_signature(signature)
        signature_bytes = int_to_bytes(r, 32) + int_to_bytes(s, 32)

        return 0, bytes(signature_bytes)

    def atcab_random(self):
        # generate a list of 32 random bytes
        random_data = [random.randint(0, 255) for _ in range(32)]
        return 0, bytearray(random_data)

    def atcab_verify(self, data_hash, signature, public_key=None) -> tuple[int, bool]:
        """Verify an ECDSA signature using either the provided public key or instance public key.

        Args:
            signature: 64-byte signature (r|s format)
            data_hash: The pre-computed SHA256 hash to verify
            public_key: Optional bytes of public key in X962 uncompressed format (64 bytes without prefix)
                       If not provided, uses the instance's public key

        Returns:
            tuple: (status, verified) where status is 0 for success and verified is True if signature is valid
        """
        try:
            # Convert signature from r|s format to DER format
            r = int.from_bytes(signature[:32], byteorder='big')
            s = int.from_bytes(signature[32:], byteorder='big')
            der_signature = utils.encode_dss_signature(r, s)

            # Get the verifying key
            verifying_key = self.public_key
            if public_key is not None:
                # Add 0x04 prefix for uncompressed point format
                public_key_with_prefix = b'\x04' + public_key
                verifying_key = ec.EllipticCurvePublicKey.from_encoded_point(
                    ec.SECP256R1(),
                    public_key_with_prefix
                )

            # Verify the signature
            verifying_key.verify(
                der_signature,
                data_hash,  # Data should already be hashed
                ec.ECDSA(utils.Prehashed(hashes.SHA256()))
            )
            return 0, True

        except Exception as e:
            log.error(f"Signature verification failed: {e}")
            return 0, False
