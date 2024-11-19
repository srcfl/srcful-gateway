# tests for server.web.handler.get.logger

from unittest.mock import Mock
import pytest
import json
from server.web.handler.requestData import RequestData
from server.web.handler.get.hello import Handler
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState

@pytest.fixture
def request_data():
    return RequestData(BlackBoard(Mock(spec=CryptoState)), {}, {}, {})

def test_logger(request_data):
    handler = Handler()
    status_code, response = handler.do_get(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert len(response) > 0
