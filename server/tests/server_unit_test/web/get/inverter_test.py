# tests for server.web.handler.get.logger

import pytest
import json
from server.inverters.modbus import Modbus
from server.web.handler.requestData import RequestData
from server.web.handler.get.inverter import Handler
from server.blackboard import BlackBoard


@pytest.fixture
def request_data():
    class MockInverter:
        def get_config_dict(self):
            assert "get_config_dict" in dir(Modbus)
            return {"test": "test"}

        def is_open(self):
            assert "is_open" in dir(Modbus)
            return True

    bb = BlackBoard()
    bb.inverters.add(MockInverter())

    return RequestData(bb, {}, {}, {})


def test_inverter(request_data):
    handler = Handler()
    status_code, response = handler.do_get(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response == {"test": "test", "status": "open"}
