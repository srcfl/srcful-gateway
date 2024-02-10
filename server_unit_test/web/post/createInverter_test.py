from server.web.handler.post.inverterTCP import Handler as TCPHandler
from server.web.handler.post.inverterRTU import Handler as RTUHandler

from server.web.handler.requestData import RequestData
from server.tasks.openInverterTask import OpenInverterTask
from server.blackboard import BlackBoard

import queue


def test_post_create_inverter_tcp():
    conf = {"ip": "192.168.10.20", "port": 502, "type": "solaredge", "address": 1}

    handler = TCPHandler()
    q = queue.Queue()
    rd = RequestData(BlackBoard(), {}, {}, conf, q)

    handler.do_post(rd)

    # check that the open inverter task was created
    assert q.qsize() == 1
    task = q.get_nowait()
    assert isinstance(task, OpenInverterTask)

    assert task.inverter.get_config()[1:] == (
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

    rd = RequestData(BlackBoard(), {}, {}, conf, q)

    handler.do_post(rd)
    assert q.qsize() == 1
    task = q.get_nowait()
    assert isinstance(task, OpenInverterTask)

    assert task.inverter.get_config()[1:] == (
        conf["port"],
        conf["baudrate"],
        conf["bytesize"],
        conf["parity"],
        conf["stopbits"],
        conf["type"],
        conf["address"],
    )