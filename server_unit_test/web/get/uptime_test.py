import pytest
import json
import logging
from server.web.handler.requestData import RequestData
from server.web.handler.get.uptime import Handler
from server.blackboard import BlackBoard

@pytest.fixture
def request_data():
    return RequestData(BlackBoard(), {}, {}, {})

def test_uptime(request_data):
    handler = Handler()
    status_code, response = handler.do_get(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert len(response) > 0
