# tests for server.web.handler.get.logger

import pytest
import json
from server.inverters.der import DER
from server.web.handler.requestData import RequestData
from server.web.handler.get.inverter import Handler
from server.blackboard import BlackBoard


@pytest.fixture
def request_data():
    class MockDER:
        def get_config(self):
            assert "get_config" in dir(DER)
            return {"test": "test"}

        def is_open(self):
            assert "is_open" in dir(DER)
            return True

    bb = BlackBoard()
    bb.devices.add(MockDER())

    return RequestData(bb, {}, {}, {})


def test_inverter(request_data):
    handler = Handler()
    status_code, response = handler.do_get(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response == {"test": "test", "status": "open"}
