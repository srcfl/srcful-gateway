from io import BytesIO
import pytest 

from server.devices.P1Telnet import P1Telnet



        

class DataReader:
    def __init__(self, data):
        self.data = BytesIO(data.encode('ascii'))

    def read_until(self, delimiter, timeout):
        result = b''
        while True:
            char = self.data.read(1)
            if not char:
                break
            result += char
            if char == delimiter:
                break
        return result
    
    def close(self):
        pass

    def get_socket(self):
        return "test_socket"
    
    def clear_buffer(self):
        pass
    
class MockTelnet:
    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout

    def connect(self):
        return True
    
    def read_until(self, delimiter, timeout):
        return DataReader(self.data).read_until(delimiter, timeout)

# set to test_ to try real harvesting
def real_harvest():
    p1 = P1Telnet("192.168.0.30", 23, "")
    assert p1.connect()
    harvest = p1.read_harvest_data(False)
    p1.disconnect()

    assert p1.meter_serial_number is not None
    assert p1.meter_serial_number == harvest['serial_number']
    assert harvest is not None
    assert harvest['serial_number'] is not None
    assert len(harvest['rows']) > 0

# real scan
def real_find_device():
    p1 = P1Telnet("192.168.0.30", 23, "abc123")
    try:
        found = p1.find_device()
        assert found is not None
        assert found.model_name == "home_wizard_p1"
    except Exception as e:
        assert False


def test_parse_p1_data():
    p1 = P1Telnet("192.168.0.30", 23, "")
    harvest = p1._parse_p1_message(get_p1_data())
    assert harvest is not None
    assert harvest['serial_number'] == "LGF5E360"
    assert len(harvest['rows']) == 28
    assert harvest['rows'][-1] == '!A267'

def test_read_harvest_data():
    mock_telnet = DataReader(get_p1_data())
    p1 = P1Telnet("192.168.0.30", 23, "")
    harvest = p1._read_harvest_data(mock_telnet)
    assert '/LGF5E360' in harvest
    assert '!A267' in harvest

    

def get_p1_data():

    return """
/LGF5E360

0-0:1.0.0(241015201510W)
1-0:1.8.0(00007225.264kWh)
1-0:2.8.0(00000000.000kWh)
1-0:3.8.0(00000003.885kVArh)
1-0:4.8.0(00001466.506kVArh)
1-0:1.7.0(0000.716kW)
1-0:2.7.0(0000.000kW)
1-0:3.7.0(0000.000kVAr)
1-0:4.7.0(0000.179kVAr)
1-0:21.7.0(0000.071kW)
1-0:22.7.0(0000.000kW)
1-0:41.7.0(0000.636kW)
1-0:42.7.0(0000.000kW)
1-0:61.7.0(0000.008kW)
1-0:62.7.0(0000.000kW)
1-0:23.7.0(0000.000kVAr)
1-0:24.7.0(0000.062kVAr)
1-0:43.7.0(0000.000kVAr)
1-0:44.7.0(0000.100kVAr)
1-0:63.7.0(0000.000kVAr)
1-0:64.7.0(0000.016kVAr)
1-0:32.7.0(234.3V)
1-0:52.7.0(233.6V)
1-0:72.7.0(234.7V)
1-0:31.7.0(000.4A)
1-0:51.7.0(002.7A)
1-0:71.7.0(000.0A)
!A267
"""

