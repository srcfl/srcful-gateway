from unittest.mock import Mock, patch
import pytest
import json
from server.web.handler.requestData import RequestData
from server.web.handler.post.initialize import Handler
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
import server.crypto.crypto as crypto

@pytest.fixture
def request_data():
    obj = {'wallet': 'd785ae2b8cf827413bbadf638d22eeae'}
    return RequestData(BlackBoard(Mock(spec=CryptoState)), {}, {}, obj)

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
    