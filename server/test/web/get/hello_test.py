# tests for server.web.handler.get.logger

import pytest
import json
import logging
from server.web.handler.requestData import RequestData
from server.web.handler.get.hello import Handler
from server.blackboard import BlackBoard

@pytest.fixture
def request_data():
    return RequestData(BlackBoard(), {}, {}, {}, None)

def test_logger(request_data):
    handler = Handler()
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert len(response) > 0
