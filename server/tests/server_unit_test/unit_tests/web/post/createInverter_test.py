from server.web.handler.post.modbus_create import Handler as ModbusDeviceHandler
from server.web.handler.requestData import RequestData
from server.tasks.openDeviceTask import OpenDeviceTask
from server.blackboard import BlackBoard
import server.tests.config_defaults as cfg


def test_post_create_inverter_tcp():
    tcp_args = cfg.TCP_ARGS
    tcp_config = cfg.TCP_CONFIG

    handler = ModbusDeviceHandler()
    rd = RequestData(BlackBoard(), {}, {}, tcp_args)

    handler.do_post(rd)

    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenDeviceTask)
    assert task.device.get_config() == tcp_config
    

def test_post_create_inverter_rtu():
    rtu_args = cfg.RTU_ARGS
    rtu_config = cfg.RTU_CONFIG

    handler = ModbusDeviceHandler()
    rd = RequestData(BlackBoard(), {}, {}, rtu_args)

    handler.do_post(rd)
    
    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenDeviceTask)
    assert task.device.get_config() == rtu_config


def test_post_create_inverter_solarman():
    solarman_args = cfg.SOLARMAN_ARGS
    solarman_config = cfg.SOLARMAN_CONFIG
    
    handler = ModbusDeviceHandler()
    rd = RequestData(BlackBoard(), {}, {}, solarman_args)

    handler.do_post(rd)
    
    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenDeviceTask)
    assert task.device.get_config() == solarman_config  
    