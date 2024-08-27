import threading

import server.tasks.harvest as harvest
from server.inverters.ModbusTCP import ModbusTCP
from server.blackboard import BlackBoard

from .modbus_sim import server


def test_execute_harvest_incremental_backoff_server_does_not_reply():
    # we start a real modbus server and connect to it
    # start a thread for the server

    server_thread = threading.Thread(target=lambda: server.start_server(5021))
    server.should_reply(False)
    server_thread.start()

    inverter = ModbusTCP(("localhost", 5021, "solaredge", 1))
    inverter._open(reconnect_delay=0, retries=0, timeout=0.1, reconnect_delay_max=0)

    # this inverter allows for connecting and one harvest (3 reads) read before it disconnects


    t = harvest.Harvest(0, BlackBoard(), inverter)

    i = 0
    while t.backoff_time < t.max_backoff_time and i < 10:
        ret = t.execute(17)
        i += 1

    # we should not have been able to read 100 times before the backoff time is maxed out
    assert i < 100

    assert inverter._is_terminated() is False

    # the next call therminates the inverter
    ret = t.execute(17)
    assert inverter._is_terminated() is True



def test_execute_harvest_server_disconnects():
    # we start a real modbus server and connect to it
    # start a thread for the server
    server_thread = threading.Thread(target=lambda: server.start_server(5022))
    server_thread.start()

    inverter = ModbusTCP(("localhost", 5022, "solaredge", 1))
    inverter._open(reconnect_delay=0, retries=0, timeout=0.1, reconnect_delay_max=0)

    server.stop_server()
    server_thread.join(1)

    # this inverter allows for connecting and one harvest (3 reads) read before it disconnects
    bb = BlackBoard()
    t = harvest.Harvest(0, bb, inverter)

    i = 0
    while t.backoff_time < t.max_backoff_time and i < 100:
        ret = t.execute(bb.time_ms())
        i += 1

    # we should not have been able to read 100 times before the backoff time is maxed out
    assert i < 100
  
    # the next call closes the connection if it has not already been closed
    # if inverter.is_open():
    #     ret = t.execute(17)
    #     assert inverter.is_open() is False

    # we can now start the server again
    server_thread = threading.Thread(target=lambda: server.start_server(5022))
    server_thread.start()

    # this call should open the connection again
    ret = t.execute(bb.time_ms())
    assert inverter._is_open() is True

    # we are now reconnected and should be able to read once again
    ret = t.execute(bb.time_ms())

    assert t.backoff_time < t.max_backoff_time

    server.stop_server()
    server_thread.join(3)

