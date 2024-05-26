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
    chip_info = {
        "deviceName": "test_chip",
        "serialNumber": b"deadbeef".hex(),
        "publicKey": public_key.hex(),
        "chipDeathCount": bb.chip_death_count
    }

    mock_chip_instance = mock_chip_class.return_value.__enter__.return_value
    mock_chip_instance.get_chip_info.return_value = chip_info
    mock_chip_instance.get_public_key.return_value = public_key

    code, result = handler.do_get(RequestData(bb, {}, {}, {}))

    assert mock_chip_instance.get_chip_info.called
    assert code == 200
    assert result == json.dumps(chip_info)
