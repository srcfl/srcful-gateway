from server.web.handler.post.modbusDevice import Handler as ModbusDeviceHandler
from server.web.handler.requestData import RequestData
from server.tasks.openDeviceTask import OpenDeviceTask
from server.blackboard import BlackBoard

import queue


def test_post_create_inverter_tcp():
    conf = {"connection": "TCP", "host": "192.168.10.20", "port": 502, "type": "solaredge", "address": 1}

    handler = ModbusDeviceHandler()
    rd = RequestData(BlackBoard(), {}, {}, conf)

    handler.do_post(rd)

    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenDeviceTask)
    c = task.device.get_config()
    assert task.device.get_config() == conf
    

def test_post_create_inverter_rtu():
    conf = {
        "connection": "RTU",
        "port": "/dev/ttyUSB0",
        "baudrate": 115200,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1,
        "type": "solaredge",
        "address": 1,
    }

    handler = ModbusDeviceHandler()
    rd = RequestData(BlackBoard(), {}, {}, conf)

    handler.do_post(rd)
    
    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenDeviceTask)
    assert task.device.get_config() == conf


def test_post_create_inverter_solarman():
    conf = {
        "connection": "SOLARMAN",
        "type": "deye",
        "serial": 1234567890,
        "address": 1,
        "host":"192.168.10.20",
        "port": 502
    }
    
    handler = ModbusDeviceHandler()
    rd = RequestData(BlackBoard(), {}, {}, conf)

    handler.do_post(rd)
    
    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenDeviceTask)
    assert task.device.get_config() == conf
    