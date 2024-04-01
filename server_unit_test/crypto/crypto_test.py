from server.crypto import crypto
import base64


def test_init_chip_release():
    # we just call to see that code can exectute
    # asserting on linux will cause failed test case as the lib actually works
    crypto.init_chip()
    crypto.release()


def test_get_header_format():
    crypto.init_chip()
    header = crypto.build_header("huawei")
    crypto.release()
    assert "alg" in header
    assert "typ" in header
    assert "opr" in header
    assert "device" in header


def test_build_header_contents():
    crypto.init_chip()
    header = crypto.build_header("huawei")
    crypto.release()
    assert header["alg"] == "ES256"
    assert header["typ"] == "JWT"
    assert header["opr"] == "production"


def test_get_device_name():
    crypto.init_chip()
    device_name = crypto.get_device_name()
    crypto.release()
    assert device_name in ['ATECC108A', 'ATECC508A', 'ATECC608', 'ATSHA204A', 'ATSHA204A', 'ATSHA206A',
                           'ECC204', 'ECC204', 'TA010', 'SHA104', 'SHA105', 'UNKNOWN']


def test_get_serial_number():
    crypto.init_chip()
    serial_number = crypto.get_serial_number()
    crypto.release()
    assert len(serial_number) == 9


def test_public_key_2_pem():
    crypto.init_chip()
    public_key = 'Hello World!'.encode('utf-8')
    pem = crypto.public_key_2_pem(public_key)
    crypto.release()
    expected = base64.b64encode(public_key).decode("ascii")
    assert expected in pem


def test_get_public_key():
    crypto.init_chip()
    public_key = crypto.get_public_key()
    crypto.release()
    assert len(public_key) == 64


def test_get_chip_info():
    crypto.init_chip()
    chip_info = crypto.get_chip_info()
    crypto.release()
    assert "deviceName" in chip_info
    assert "serialNumber" in chip_info
    assert "publicKey" in chip_info


def test_get_signature():
    crypto.init_chip()
    signature = crypto.get_signature("Hello World!")
    crypto.release()
    assert len(signature) == 64

def test_get_jwt():
    crypto.init_chip()
    jwt = crypto.build_jwt("Hello World!", "volvo")
    crypto.release()
    assert jwt is not None
    assert len(jwt) > 0
    assert jwt.count('.') == 2
