from unittest.mock import patch
from server.crypto import crypto
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


@patch('server.crypto.crypto.init_chip')
@patch('server.crypto.crypto.get_chip_info')
@patch('server.crypto.crypto.get_public_key')
@patch('server.crypto.crypto.release')
def test_get(mock_release, mock_getPublicKey, mock_getChipInfo, mock_initChip):
  handler = get_crypto.Handler()
  public_key = bytearray(64)
  chipInfo = {'deviceName': 'test_chip',
              'serialNumber': b'deadbeef'.hex(), 'publicKey': public_key.hex()}

  mock_getChipInfo.return_value = chipInfo
  mock_getPublicKey.return_value = public_key

  result = handler.do_get(None)
  mock_initChip.assert_called_once()
  mock_getChipInfo.assert_called_once_with()
  mock_release.assert_called_once()
  chipInfo['publicKey_pem'] = crypto.public_key_2_pem(public_key)
  assert result[0] == 200
  assert result[1] == json.dumps(chipInfo)
