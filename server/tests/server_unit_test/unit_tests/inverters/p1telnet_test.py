import pytest 

from server.devices.P1Telnet import P1Telnet


# set to test_ to try real harvesting
def real_harvest():
    p1 = P1Telnet("192.168.0.30", 23, "")
    assert p1.connect()
    harvest = p1.read_harvest_data(False)
    p1.disconnect()

    assert p1.id is not None
    assert p1.id == harvest['serial_number']
    assert harvest is not None
    assert harvest['serial_number'] is not None
    assert len(harvest['rows']) > 0
