from server.inverters.InverterTCP import InverterTCP
from server.inverters.InverterRTU import InverterRTU

from server.web.post.inverterTCP import Handler as TCPHandler
from server.web.post.inverterRTU import Handler as RTUHandler

import queue

def test_post_create_InverterTCP():
    conf = {'ip': '192.168.10.20', 
            'port': 502, 
            'type': 'solaredge', 
            'address': 1}
    
    handler = TCPHandler()

    handler.doPost(conf, None, queue.Queue())

    assert handler.inverter.getConfig()[1:] == (conf['ip'], conf['port'], conf['type'], conf['address'])


def test_post_create_InverterRTU():
    conf = {'port': '/dev/ttyUSB0', 
            'baudrate': 115200, 
            'bytesize': 8, 
            'parity': 'N', 
            'stopbits': 1, 
            'type': 'solaredge', 
            'address': 1}
    
    handler = RTUHandler()

    handler.doPost(conf, None, queue.Queue())

    assert handler.inverter.getConfig()[1:] == (conf['port'], conf['baudrate'], conf['bytesize'], conf['parity'], conf['stopbits'], conf['type'], conf['address'])