from server.web.handler.post.modbusTCP import Handler as TCPHandler
from server.web.handler.post.modbusRTU import Handler as RTUHandler

from server.web.handler.requestData import RequestData
from server.tasks.openInverterTask import OpenInverterTask
from server.blackboard import BlackBoard

import queue


def test_post_create_inverter_tcp():
    conf = {"ip": "192.168.10.20", "port": 502, "type": "solaredge", "address": 1}

    handler = TCPHandler()
    rd = RequestData(BlackBoard(), {}, {}, conf)

    handler.do_post(rd)

    # check that the open inverter task was created
    tasks = rd.bb.purge_tasks()
    assert len(tasks) == 1
    task = tasks[0]
    assert isinstance(task, OpenInverterTask)

    assert task.der._get_config()[1:] == (
        conf["ip"],
        conf["port"],
        conf["type"],
        conf["address"],
    )


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
