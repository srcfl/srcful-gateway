import pytest
from unittest.mock import MagicMock, Mock
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.tasks.openDeviceTask import OpenDeviceTask
import server.tests.config_defaults as cfg
from server.web.handler.post.device import Handler as DeviceHandler
from server.web.handler.requestData import RequestData

@pytest.fixture
def device_config():
    data = MagicMock()
    data.data = cfg.TCP_ARGS
    return data

@pytest.fixture
def handler():
    return DeviceHandler()

def test_create_device(device_config, handler):
    response = handler.do_post(device_config)
    
    assert response[0] == 200
    
    
def test_post_create_p1_telnet():
    conf = cfg.P1_TELNET_CONFIG
    
    handler = DeviceHandler()
    rd = RequestData(BlackBoard(Mock(spec=CryptoState)), {}, {}, conf)

    handler.do_post(rd)
    
    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenDeviceTask)
    assert task.device.get_config() == cfg.P1_TELNET_CONFIG