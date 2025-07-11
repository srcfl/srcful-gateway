import bluetooth.macAddr


def test_macAddr():
    assert len(bluetooth.macAddr.get()) == 17
