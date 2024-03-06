from server.crypto import crypto


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


def test_get_header_contents():
    crypto.init_chip()
    header = crypto.build_header("huawei")
    crypto.release()
    assert header["alg"] == "ES256"
    assert header["typ"] == "JWT"
    assert header["opr"] == "production"
