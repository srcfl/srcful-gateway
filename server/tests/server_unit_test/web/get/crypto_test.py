from unittest.mock import patch
import server.web.handler.get.crypto as get_crypto
from server.blackboard import BlackBoard
from server.web.handler.requestData import RequestData
import pytest
import json


@pytest.fixture
def mock_initChip():
  pass


@pytest.fixture
def mock_getChipInfo(data):
  pass


@pytest.fixture
def mock_release():
    pass


@patch("server.crypto.crypto.Chip", autospec=True)
def test_get(mock_chip_class):
    handler = get_crypto.Handler()
    bb = BlackBoard()

    bb.increment_chip_death_count()

    public_key = bytearray(64)
    serial_no = b"deadbeef"
    expected = {
        handler.DEVICE: "test_chip",
        handler.SERIAL_NO: b"deadbeef".hex(),
        handler.PUBLIC_KEY: public_key.hex(),
        handler.COMPACT_KEY: public_key[:32].hex(),
        handler.CHIP_DEATH_COUNT: bb.chip_death_count
    }

    mock_chip_instance = mock_chip_class.return_value.__enter__.return_value
    mock_chip_instance.get_device_name.return_value = "test_chip"
    mock_chip_instance.get_serial_number.return_value = serial_no
    mock_chip_instance.get_public_key.return_value = public_key
    mock_chip_instance.public_key_to_compact.return_value = public_key[:32]

    code, result = handler.do_get(RequestData(bb, {}, {}, {}))

    assert code == 200
    assert result == json.dumps(expected)
