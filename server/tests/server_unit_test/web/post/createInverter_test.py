from unittest.mock import Mock
from server.crypto.crypto_state import CryptoState
from server.web.handler.post.device import Handler as DeviceHandler
from server.web.handler.requestData import RequestData
from server.tasks.openDeviceTask import OpenDeviceTask
from server.app.blackboard import BlackBoard
import server.tests.config_defaults as cfg
import pytest
from server.crypto.crypto_state import CryptoState

@pytest.fixture
def bb():
    return BlackBoard(Mock(spec=CryptoState))


def test_post_create_inverter_tcp(bb: BlackBoard):
    conf = cfg.TCP_CONFIG

    handler = DeviceHandler()
    rd = RequestData(bb, {}, {}, conf)

    handler.do_post(rd)

    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenDeviceTask)
    assert task.device.get_config() == conf
    

# def test_post_create_inverter_rtu():
#     conf = cfg.RTU_CONFIG

#     handler = DeviceHandler()
#     rd = RequestData(BlackBoard(), {}, {}, conf)

#     handler.do_post(rd)
    
#     # check that the open inverter task was created
#     tasks = rd.bb.purge_tasks()
#     assert len(tasks) == 1
#     task = tasks[0]
#     assert isinstance(task, OpenDeviceTask)
#     assert task.device.get_config() == conf


def test_post_create_inverter_solarman(bb: BlackBoard):
    conf = cfg.SOLARMAN_CONFIG
    
    handler = DeviceHandler()
    rd = RequestData(bb, {}, {}, conf)

    handler.do_post(rd)
    
    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenDeviceTask)
    assert task.device.get_config() == conf
    