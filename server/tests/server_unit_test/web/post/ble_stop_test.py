from unittest.mock import Mock
import pytest
import json
from server.crypto.crypto_state import CryptoState
from server.web.handler.requestData import RequestData
from server.web.handler.post.ble_stop import Handler
from server.app.blackboard import BlackBoard


@pytest.fixture
def request_data(blackboard):
    return RequestData(blackboard, {}, {}, {})


def test_do_post(request_data):
    handler = Handler()
    status_code, response = handler.do_post(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert "status" in response
    assert response["status"] == "success"
    assert "message" in response
