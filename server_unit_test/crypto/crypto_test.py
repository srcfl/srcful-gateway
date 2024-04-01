from server.crypto import crypto
import base64


def test_init_chip_release():
    # we just call to see that code can exectute
    # asserting on linux will cause failed test case as the lib actually works
    with crypto.Chip() as chip:
        chip.base64_url_encode(b"Hello World!")


def test_get_header_format():
    with crypto.Chip() as chip:
        header = chip.build_header("huawei")
    assert "alg" in header
    assert "typ" in header
    assert "opr" in header
    assert "device" in header


def test_build_header_contents():
    with crypto.Chip() as chip:
        header = chip.build_header("huawei")
    assert header["alg"] == "ES256"
    assert header["typ"] == "JWT"
    assert header["opr"] == "production"


def test_get_device_name():
    with crypto.Chip() as chip:
        device_name = chip.get_device_name()
    assert device_name in ['ATECC108A', 'ATECC508A', 'ATECC608', 'ATSHA204A', 'ATSHA204A', 'ATSHA206A',
                           'ECC204', 'ECC204', 'TA010', 'SHA104', 'SHA105', 'UNKNOWN']


def test_get_serial_number():
    with crypto.Chip() as chip:
        serial_number = chip.get_serial_number()
    assert len(serial_number) == 9


def test_public_key_2_pem():
    public_key = 'Hello World!'.encode('utf-8')
    with crypto.Chip() as chip:
        pem = chip.public_key_2_pem(public_key)
    expected = base64.b64encode(public_key).decode("ascii")
    assert expected in pem


def test_get_public_key():
    with crypto.Chip() as chip:
        public_key = chip.get_public_key()
    assert len(public_key) == 64


def test_get_chip_info():
    with crypto.Chip() as chip:
        chip_info = chip.get_chip_info()
    assert "deviceName" in chip_info
    assert "serialNumber" in chip_info
    assert "publicKey" in chip_info


def test_get_signature():
    with crypto.Chip() as chip:
        signature = chip.get_signature("Hello World!")
        assert len(signature) == 64

def test_get_jwt():
    with crypto.Chip() as chip:
        jwt = chip.build_jwt("Hello World!", "volvo")
    assert jwt is not None
    assert len(jwt) > 0
    assert jwt.count('.') == 2
