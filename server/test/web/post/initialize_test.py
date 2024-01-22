import pytest
import json
import logging
from server.web.handler.requestData import RequestData
from server.web.handler.post.initialize import Handler
from server.blackboard import BlackBoard

@pytest.fixture
def request_data():
    obj = {'wallet': 'd785ae2b8cf827413bbadf638d22eeae'}
    return RequestData(BlackBoard(), {}, {}, obj, None)

def test_initialize(request_data):
    handler = Handler()

    status_code, response = handler.do_post(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response == {'initialized': False}
    