# test for server.web.handler.post.wifi
from server.web.handler.post.wifi import Handler
from server.web.handler.requestData import RequestData
from server.blackboard import BlackBoard
from server.tasks.openWiFiConTask import OpenWiFiConTask
import json
import queue


def mock__init__(self, SSID, PSK):
    pass

#@patch.object(WifiHandler, '__init__', mock__init__)
def test_doPost():
    data_params = {
        "ssid": "test",
        "psk": "test",
    }
    tasks = queue.PriorityQueue()
    request_data = RequestData(BlackBoard(), post_params={}, query_params={}, data=data_params)

    handler = Handler()

    status_code, response = handler.do_post(request_data)

    tasks = request_data.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenWiFiConTask)

    assert status_code == 200
    assert json.loads(response) == {"status": "ok"}

def test_doPost_bad_data():
    data_params = {
        "sssid": "test",
        "password": "test",
    }
    tasks = queue.PriorityQueue()
    request_data = RequestData(BlackBoard(), post_params={}, query_params={}, data=data_params)

    handler = Handler()

    status_code, response = handler.do_post(request_data)

    assert status_code == 400
    assert tasks.qsize() == 0