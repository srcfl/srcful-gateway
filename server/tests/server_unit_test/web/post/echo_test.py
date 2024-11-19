from unittest.mock import Mock
import pytest
import json
from server.crypto.crypto_state import CryptoState
from server.web.handler.requestData import RequestData
from server.web.handler.post.echo import Handler
from server.app.blackboard import BlackBoard

@pytest.fixture
def request_data():
    return RequestData(BlackBoard(Mock(spec=CryptoState)), {}, {}, {"sent": "thedata"})

def test_logger(request_data):
    handler = Handler()
    status_code, response = handler.do_post(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response == {"echo": request_data.data}
