from server.web.handler.post.device import Handler as DeviceHandler
from server.web.handler.requestData import RequestData
from server.tasks.openDeviceTask import OpenDeviceTask
from server.blackboard import BlackBoard
import server.tests.config_defaults as cfg

import queue


def test_post_create_inverter_tcp():
    conf = cfg.TCP_CONFIG

    handler = DeviceHandler()
    rd = RequestData(BlackBoard(), {}, {}, conf)

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


def test_post_create_inverter_solarman():
    conf = cfg.SOLARMAN_CONFIG
    
    handler = DeviceHandler()
    rd = RequestData(BlackBoard(), {}, {}, conf)

    handler.do_post(rd)
    
    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenDeviceTask)
    assert task.device.get_config() == conf
    