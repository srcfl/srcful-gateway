from unittest.mock import Mock
import pytest
import json
from server.crypto.crypto_state import CryptoState
from server.web.handler.requestData import RequestData
from server.web.handler.post.settings import Handler
from server.app.blackboard import BlackBoard


@pytest.fixture
def request_data(blackboard):
    new_settings = {
        "settings": {
            "harvest": {
                "endpoints": ["https://example.com/harvest"]
            }
        }
    }

    return RequestData(blackboard, {}, {}, new_settings)


def test_settings(request_data):

    handler = Handler()
    status_code, response = handler.do_post(request_data)

    assert status_code == 200
    response = json.loads(response)
    assert response == {'success': True}
