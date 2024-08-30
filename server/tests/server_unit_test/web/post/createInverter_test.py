from server.web.handler.post.modbusDevice import Handler as ModbusDeviceHandler
from server.web.handler.requestData import RequestData
from server.tasks.openInverterTask import OpenInverterTask
from server.blackboard import BlackBoard

import queue


def test_post_create_inverter_tcp():
    conf = {"mode": "TCP", "ip": "192.168.10.20", "port": 502, "type": "solaredge", "address": 1}

    handler = ModbusDeviceHandler()
    rd = RequestData(BlackBoard(), {}, {}, conf)

    handler.do_post(rd)

    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenInverterTask)
    ret_conf = task.der.get_config()
    
    assert ret_conf == conf
    
    
    
    # assert task.der.get_config()[1:] == (
    #     conf["mode"],
    #     conf["ip"],
    #     conf["port"],
    #     conf["type"],
    #     conf["address"],
    # )


def test_post_create_inverter_rtu():
    conf = {
        "port": "/dev/ttyUSB0",
        "baudrate": 115200,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1,
        "type": "solaredge",
        "address": 1,
    }

    handler = RTUHandler()
    # check that the open inverter task was created
    q = queue.Queue()

    rd = RequestData(BlackBoard(), {}, {}, conf)

    handler.do_post(rd)
    
    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenInverterTask)

    assert task.der._get_config()[1:] == (
        conf["port"],
        conf["baudrate"],
        conf["bytesize"],
        conf["parity"],
        conf["stopbits"],
        conf["type"],
        conf["address"],
    )
