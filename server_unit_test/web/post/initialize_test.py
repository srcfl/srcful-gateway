from unittest.mock import patch

import pytest
import json
from server.web.handler.requestData import RequestData
from server.web.handler.post.initialize import Handler
from server.blackboard import BlackBoard

import server.crypto.crypto as crypto

@pytest.fixture
def request_data():
    obj = {'wallet': 'd785ae2b8cf827413bbadf638d22eeae'}
    return RequestData(BlackBoard(), {}, {}, obj)

def test_initialize(request_data):

    with patch("server.crypto.crypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.atcab_read_serial_number", return_value=crypto.ATCA_SUCCESS):
            with patch("server.crypto.crypto.atcab_sign", return_value=crypto.ATCA_SUCCESS):

                handler = Handler()
                status_code, response = handler.do_post(request_data)  

    assert status_code == 200
    response = json.loads(response)
    assert response == {'initialized': False}
    