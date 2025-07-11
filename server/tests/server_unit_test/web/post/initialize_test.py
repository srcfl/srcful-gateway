from unittest.mock import Mock, patch
import pytest
import json
from server.web.handler.requestData import RequestData
from server.web.handler.post.initialize import Handler
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
import server.crypto.crypto as crypto


@pytest.fixture
def request_data(blackboard):
    obj = {'wallet': 'd785ae2b8cf827413bbadf638d22eeae'}
    return RequestData(blackboard, {}, {}, obj)


def test_initialize(request_data):

    with patch("server.crypto.crypto.HardwareCrypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.HardwareCrypto.atcab_read_serial_number", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            with patch("server.crypto.crypto.HardwareCrypto.atcab_sign", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                with patch("server.crypto.crypto.HardwareCrypto.atcab_get_pubkey", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                    handler = Handler()
                    status_code, response = handler.do_post(request_data)

    assert status_code == 200
    response = json.loads(response)
    assert response == {'initialized': False}


def test_intialize_no_internet(request_data):
    with patch("server.network.network_utils.NetworkUtils.has_internet_access", return_value=False):
        with patch("server.crypto.crypto.HardwareCrypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
            with patch("server.crypto.crypto.HardwareCrypto.atcab_read_serial_number", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                with patch("server.crypto.crypto.HardwareCrypto.atcab_sign", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                    with patch("server.crypto.crypto.HardwareCrypto.atcab_get_pubkey", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
                        handler = Handler()
                        status_code, response = handler.do_post(request_data)

    assert status_code == 200
    response = json.loads(response)
    assert 'idAndWallet' in response
    assert 'signature' in response


def test_initialize_no_wallet(blackboard):
    request_data = RequestData(blackboard, {}, {}, {})
    handler = Handler()
    status_code, response = handler.do_post(request_data)

    assert status_code == 400
    response = json.loads(response)
    assert 'status' in response
    assert response['status'] == 'error'
