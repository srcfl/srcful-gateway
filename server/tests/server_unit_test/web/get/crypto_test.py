from unittest.mock import patch
import server.web.handler.get.crypto as get_crypto
from server.app.blackboard import BlackBoard
from server.web.handler.requestData import RequestData
import pytest
import json
import server.crypto.crypto as crypto


@pytest.fixture
def mock_initChip():
  pass


@pytest.fixture
def mock_getChipInfo(data):
  pass


@pytest.fixture
def mock_release():
    pass


def test_get():
    handler = get_crypto.Handler()
    bb = BlackBoard()

    bb.increment_chip_death_count()

    with patch('server.crypto.crypto.HardwareCrypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.HardwareCrypto.atcab_read_serial_number', return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            with patch('server.crypto.crypto.HardwareCrypto.atcab_get_pubkey', return_value=(crypto.ATCA_SUCCESS, b'0000000000000000000000000000000000000000000000000000000000000000')):

              code, result = handler.do_get(RequestData(bb, {}, {}, {}))

    assert code == 200
