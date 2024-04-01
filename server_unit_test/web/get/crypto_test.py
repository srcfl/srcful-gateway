from unittest.mock import patch
import server.web.handler.get.crypto as get_crypto
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

    public_key = bytearray(64)
    chip_info = {
        "deviceName": "test_chip",
        "serialNumber": b"deadbeef".hex(),
        "publicKey": public_key.hex(),
    }

    mock_chip_instance = mock_chip_class.return_value.__enter__.return_value
    mock_chip_instance.get_chip_info.return_value = chip_info
    mock_chip_instance.get_public_key.return_value = public_key
    mock_chip_instance.public_key_2_pem.return_value = "test_pem"

    result = handler.do_get(None)

    assert mock_chip_instance.get_chip_info.called
    assert mock_chip_instance.get_public_key.called
    chip_info["publicKey_pem"] = "test_pem"
    assert result[0] == 200
    assert result[1] == json.dumps(chip_info)
