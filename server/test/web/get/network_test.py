import pytest
import json
from server.web.handler.requestData import RequestData
from server.web.handler.get.network import Handler
from server.wifi.wifi import getConnectionConfigs
from server.blackboard import BlackBoard

@pytest.fixture
def request_data():
    return RequestData(BlackBoard(), {}, {}, {}, None)

def test_logger(request_data):
    handler = Handler()
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    expected = json.loads(json.dumps({"connections":getConnectionConfigs()}))   # getConnectionConfigs() returns a list of dicts, so we need to convert it to JSON and back to a dict to compare   
    assert response == expected