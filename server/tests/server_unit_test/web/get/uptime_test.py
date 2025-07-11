from unittest.mock import Mock
import pytest
import json
from server.web.handler.requestData import RequestData
from server.web.handler.get.uptime import Handler
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState


@pytest.fixture
def request_data(blackboard):
    return RequestData(blackboard, {}, {}, {})


def test_uptime(request_data):
    handler = Handler()
    status_code, response = handler.do_get(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert len(response) > 0
