from unittest.mock import Mock
import pytest
from server.crypto.crypto_state import CryptoState
from server.web.handler.post.wifi import Handler
from server.web.handler.requestData import RequestData
from server.app.blackboard import BlackBoard
import json
import queue


def mock__init__(self, SSID, PSK):
    pass


def test_doPost(bb: BlackBoard):
    data_params = {
        "ssid": "test",
        "psk": "test",
    }
    request_data = RequestData(bb, post_params={}, query_params={}, data=data_params)

    handler = Handler()

    status_code, response = handler.do_post(request_data)

    assert status_code == 503
    assert json.loads(response) == {"status": "error", "message": "Failed to connect to WiFi"}


def test_doPost_bad_data(bb):
    data_params = {
        "sssid": "test",
        "password": "test",
    }
    tasks = queue.PriorityQueue()
    request_data = RequestData(bb, post_params={}, query_params={}, data=data_params)

    handler = Handler()

    status_code, response = handler.do_post(request_data)

    assert status_code == 422
    assert tasks.qsize() == 0
