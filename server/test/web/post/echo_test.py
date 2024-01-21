# tests for server.web.handler.get.logger

import pytest
import json
import logging
from server.web.handler.requestData import RequestData
from server.web.handler.post.echo import Handler
from server.blackboard import BlackBoard

@pytest.fixture
def request_data():
    return RequestData(BlackBoard(), {}, {}, {"sent":"thedata"}, None)

def test_logger(request_data):
    handler = Handler()
    status_code, response = handler.do_post(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response == {"echo": request_data.data}
