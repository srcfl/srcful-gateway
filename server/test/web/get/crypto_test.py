from unittest.mock import patch
from server.crypto import crypto
import server.web.get.crypto as get_crypto
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


@patch('server.crypto.crypto.initChip')
@patch('server.crypto.crypto.getChipInfo')
@patch('server.crypto.crypto.getPublicKey')
@patch('server.crypto.crypto.release')
def test_get(mock_release, mock_getPublicKey, mock_getChipInfo, mock_initChip):
  handler = get_crypto.Handler()
  public_key = bytearray(64)
  chipInfo = {'deviceName': 'test_chip',
              'serialNumber': b'deadbeef'.hex(), 'publicKey': public_key.hex()}

  mock_getChipInfo.return_value = chipInfo
  mock_getPublicKey.return_value = public_key

  result = handler.doGet({}, None, None)
  mock_initChip.assert_called_once()
  mock_getChipInfo.assert_called_once_with()
  mock_release.assert_called_once()
  chipInfo['publicKey_pem'] = crypto.publicKeyToPEM(public_key)
  assert result[0] == 200
  assert result[1] == json.dumps(chipInfo)
