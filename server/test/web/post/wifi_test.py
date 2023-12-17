# test for server.web.handler.post.wifi

import pytest
from server.web.handler.post.wifi import Handler
from server.web.handler.requestData import RequestData
import json
import queue


#from unittest.mock import patch

def mock__init__(self, SSID, PSK):
    pass

#@patch.object(WifiHandler, '__init__', mock__init__)
def test_doPost():
    data_params = {
        "ssid": "test",
        "psk": "test",
    }
    tasks = queue.PriorityQueue()
    request_data = RequestData(stats={'startTime':0, 'name':'dret'}, post_params={}, query_params={}, data=data_params, timeMSFunc=lambda: 10, chipInfoFunc=lambda: "dret", tasks=tasks)

    handler = Handler()

    status_code, response = handler.doPost(request_data)

    assert status_code == 200
    assert json.loads(response) == {"status": "ok"}
    assert tasks.qsize() == 1

def test_doPost_bad_data():
    data_params = {
        "sssid": "test",
        "password": "test",
    }
    tasks = queue.PriorityQueue()
    request_data = RequestData(stats={'startTime':0, 'name':'dret'}, post_params={}, query_params={}, data=data_params, timeMSFunc=lambda: 10, chipInfoFunc=lambda: "dret", tasks=tasks)

    handler = Handler()

    status_code, response = handler.doPost(request_data)

    assert status_code == 400
    assert tasks.qsize() == 0