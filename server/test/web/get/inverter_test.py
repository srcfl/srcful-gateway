# tests for server.web.handler.get.logger

import pytest
import json
import logging
from unittest.mock import MagicMock
from server.web.handler.requestData import RequestData
from server.web.handler.get.inverter import Handler

@pytest.fixture
def request_data():
    class mockInverter:
        def getConfigDict(self):
            return {'test': 'test'}
        def isOpen(self):
            return True
        
    return RequestData({"inverter":mockInverter()}, {}, {}, {}, None, None, None)

def test_inverter(request_data):
    handler = Handler()
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response == {'test': 'test', 'status': 'open'}
   