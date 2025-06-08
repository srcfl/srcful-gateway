from server.crypto import crypto
import base64
import pytest
from cryptography.hazmat.primitives import hashes

from unittest.mock import patch


def test_init_chip_release():
    # we just call to see that code can exectute
    # asserting on linux will cause failed test case as the lib actually works

    # we need to mock the cryptoauthlib atcab_init function to make this test work

    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):

        with crypto.Chip() as chip:
            crypto.base64_url_encode(b"Hello World!")


def test_get_header_format():

    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_read_serial_number', return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            with patch('server.crypto.crypto.HardwareCrypto.atcab_get_pubkey', return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                with patch('server.crypto.crypto.HardwareCrypto.atcab_sign', return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                    with crypto.Chip() as chip:
                        header = chip.build_header({"model": "volvo 240"})
                    assert "alg" in header
                    assert "typ" in header
                    assert "opr" in header
                    assert "device" in header


def test_init_throws_error():

    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=1), patch('server.crypto.software.SoftwareCrypto.atcab_init', return_value=1):
        with pytest.raises(crypto.ChipError) as excinfo:
            with crypto.Chip() as chip:
                pass
        assert excinfo.value.code == 1


def test_sign_throws_error():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_sign', return_value=(1, b'')), patch('server.crypto.software.SoftwareCrypto.atcab_sign', return_value=(1, b'')):
            with crypto.Chip() as chip:
                with pytest.raises(crypto.ChipError) as excinfo:
                    chip.get_signature("Hello World!")
                assert excinfo.value.code == 1


def test_error_recovery():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with crypto.Chip() as chip:
            with patch('server.crypto.crypto.HardwareCrypto.atcab_sign', return_value=(1, b'')), patch('server.crypto.software.SoftwareCrypto.atcab_sign', return_value=(1, b'')):
                with pytest.raises(crypto.ChipError) as excinfo:
                    chip.get_signature("Hello World!")
                assert excinfo.value.code == 1
            with patch('server.crypto.crypto.HardwareCrypto.atcab_sign', return_value=(crypto.ATCA_SUCCESS, b'0000000000000000000000000000000000000000000000000000000000000000')):
                sign = chip.get_signature("Hello World!")
    assert len(sign) == 64


def test_get_pubkey_throws_error():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_get_pubkey', return_value=(1, b'')), patch('server.crypto.software.SoftwareCrypto.atcab_get_pubkey', return_value=(1, b'')):
            with crypto.Chip() as chip:
                with pytest.raises(crypto.ChipError) as excinfo:
                    chip.get_public_key()
                assert excinfo.value.code == 1


def test_serial_number_throws_error():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_read_serial_number', return_value=(1, b'')), patch('server.crypto.software.SoftwareCrypto.atcab_read_serial_number', return_value=(1, b'')):
            with crypto.Chip() as chip:
                with pytest.raises(crypto.ChipError) as excinfo:
                    chip.get_serial_number()
                assert excinfo.value.code == 1


def test_build_header_contents():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_read_serial_number', return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            with patch('server.crypto.crypto.HardwareCrypto.atcab_get_pubkey', return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                with patch('server.crypto.crypto.HardwareCrypto.atcab_sign', return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                    with crypto.Chip() as chip:
                        header = chip.build_header({"model": "volvo 240"})
                    assert header["alg"] == "ES256"
                    assert header["typ"] == "JWT"
                    assert header["opr"] == "production"


def test_get_device_name():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with crypto.Chip() as chip:
            device_name = chip.get_device_name()
    assert device_name in ['ATECC108A', 'ATECC508A', 'ATECC608', 'ATSHA204A', 'ATSHA204A', 'ATSHA206A',
                           'ECC204', 'ECC204', 'TA010', 'SHA104', 'SHA105', 'UNKNOWN']


def test_get_serial_number():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_read_serial_number', return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            with crypto.Chip() as chip:
                serial_number = chip.get_serial_number()
    assert len(serial_number) == 12 or len(serial_number) == 9  # 9 for software crypto


def test_get_serial_number_retry():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_read_serial_number', return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            with crypto.Chip() as chip:
                serial_number = chip.get_serial_number(1)
    assert len(serial_number) == 12 or len(serial_number) == 9


def test_public_key_2_pem():
    public_key = 'Hello World!'.encode('utf-8')
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with crypto.Chip() as chip:
            pem = chip.public_key_2_pem(public_key)
    expected = base64.b64encode(public_key).decode("ascii")
    assert expected in pem


def test_get_public_key():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_get_pubkey', return_value=(crypto.ATCA_SUCCESS, b'0000000000000000000000000000000000000000000000000000000000000000')):
            with crypto.Chip() as chip:
                public_key = chip.get_public_key()
    assert len(public_key) == 64


def test_get_public_key_with_retry():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_get_pubkey', return_value=(crypto.ATCA_SUCCESS, b'0000000000000000000000000000000000000000000000000000000000000000')):
            with crypto.Chip() as chip:
                public_key = chip.get_public_key(retries=1)
    assert len(public_key) == 64

# def test_get_chip_info():
#     with patch('server.crypto.crypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
#         with patch('server.crypto.crypto.atcab_read_serial_number', return_value=crypto.ATCA_SUCCESS):
#             with patch('server.crypto.crypto.atcab_get_pubkey', return_value=crypto.ATCA_SUCCESS):
#                 with crypto.Chip() as chip:
#                     chip_info = chip.get_chip_info()
#     assert "deviceName" in chip_info
#     assert "serialNumber" in chip_info
#     assert "publicKey" in chip_info


def test_get_signature():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_sign', return_value=(crypto.ATCA_SUCCESS, b'0000000000000000000000000000000000000000000000000000000000000000')):
            with crypto.Chip() as chip:
                signature = chip.get_signature("Hello World!")
    assert len(signature) == 64


def test_get_signature_retry():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_sign', return_value=(crypto.ATCA_SUCCESS, b'0000000000000000000000000000000000000000000000000000000000000000')):
            with crypto.Chip() as chip:
                signature = chip.get_signature("Hello World!", 1)
    assert len(signature) == 64


def test_get_jwt():
    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_read_serial_number', return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            with patch('server.crypto.crypto.HardwareCrypto.atcab_get_pubkey', return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                with patch('server.crypto.crypto.HardwareCrypto.atcab_sign', return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                    with crypto.Chip() as chip:
                        jwt = chip.build_jwt("Hello World!", {"car": "volvo 240"})
    assert jwt is not None
    assert len(jwt) > 0
    assert jwt.count('.') == 2


def test_base64_url_encode():
    data = 'Hello World'.encode('utf-8')
    encoded = crypto.base64_url_encode(data)
    assert encoded.decode('utf-8') == "SGVsbG8gV29ybGQ"
    assert len(encoded) > 0


def test_jwtlify():
    data = {'message': 'Hello World'}
    encoded = crypto.jwtlify(data)
    assert encoded == "eyJtZXNzYWdlIjogIkhlbGxvIFdvcmxkIn0"


def test_compact_key():
    pubkey = "a3302c809a6a42d2e71f5fe6e73b70fefeb47b4e02acd9ff9de44931ad4a301f31144c6a37bdde31a333e998d7c59cd1269627b354817dbb93841bfccd1b2534"
    compact = crypto.public_key_to_compact(bytearray.fromhex(pubkey))
    expected = "112EsRY1kgy7RD3mu4UU1U3EzBJq364pALxazcEyvxTTGVJtvpFZ"
    assert compact.decode("utf-8") == expected


def test_get_random():
    software_crypto = crypto.SoftwareCrypto()
    code, random_bytes = software_crypto.atcab_random()
    assert code == crypto.ATCA_SUCCESS
    assert len(random_bytes) == 32

    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_random', return_value=(crypto.ATCA_SUCCESS, random_bytes)):
            with crypto.Chip() as chip:
                random_bytes = chip.get_random()
    assert len(random_bytes) == 32


def test_verify_signature():
    software_crypto = crypto.SoftwareCrypto()

    # Simple test message
    test_message = b"My name is Jeff"

    # Hash the message
    digest = hashes.Hash(hashes.SHA256())
    digest.update(test_message)
    message_hash = digest.finalize()

    # Sign the message
    status, signature = software_crypto.atcab_sign(0, message_hash)
    assert status == 0
    assert len(signature) == 64  # r|s format should be 64 bytes

    # Get the public key
    status, public_key = software_crypto.atcab_get_pubkey(0)
    assert status == 0

    # Verify the signature
    status, is_valid = software_crypto.atcab_verify(message_hash, signature, public_key)
    assert status == 0
    assert is_valid is True

    # Verify with wrong message should fail
    wrong_message = b"Hi Jeff"
    digest = hashes.Hash(hashes.SHA256())
    digest.update(wrong_message)
    wrong_hash = digest.finalize()

    status, is_valid = software_crypto.atcab_verify(wrong_hash, signature, public_key)
    assert status == 0
    assert is_valid is False
