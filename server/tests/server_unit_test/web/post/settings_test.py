from unittest.mock import patch

import pytest
import json
from server.web.handler.requestData import RequestData
from server.web.handler.post.settings import Handler
from server.blackboard import BlackBoard


@pytest.fixture
def request_data():
    new_settings = {
        "settings": {
            "harvest": {
                "endpoints": ["https://example.com/harvest"]
            }
        }
    }
     
    return RequestData(BlackBoard(), {}, {}, new_settings)

def test_settings(request_data):

    handler = Handler()
    status_code, response = handler.do_post(request_data)  

    assert status_code == 200
    response = json.loads(response)
    assert response == {'success': True}
    