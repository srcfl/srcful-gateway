import pytest
import json
from server.web.handler.requestData import RequestData
from server.web.handler.get.network import NetworkHandler
from server.web.handler.get.network import AddressHandler
from server.web.handler.get.network import ModbusScanHandler
from server.network.wifi import get_connection_configs
from server.blackboard import BlackBoard
from unittest.mock import patch

# To-do: Break down the test cases into smaller test cases and in their respective classes 
# (e.g. NetworkHandlerTest, AddressHandlerTest, ModbusScanHandlerTest)

@pytest.fixture
def request_data():
    bb = BlackBoard()
    bb.rest_server_port = 8081
    bb.rest_server_ip = "127.0.0.1"
    return RequestData(bb, {}, {}, {})


def test_network(request_data):
    handler = NetworkHandler()
    status_code, response = handler.do_get(request_data)
    assert status_code == 200
    response = json.loads(response)
    expected = json.loads(json.dumps({handler.CONNECTIONS:get_connection_configs()}))   # getConnectionConfigs() returns a list of dicts, so we need to convert it to JSON and back to a dict to compare   
    assert response == expected


def test_network_address(request_data):
    handler = AddressHandler()
    status_code, response = handler.do_get(request_data)
    assert status_code == 200
    response = json.loads(response)
    ip = response[handler.IP]
    
    assert ip.count(".") == 3
    for part in ip.split("."):
        assert 0 <= int(part) <= 255
    assert response[handler.PORT] == 8081

    assert response[handler.ETH0_MAC]
    assert response[handler.WLAN0_MAC]

def test_parse_ports():
    handler = ModbusScanHandler()
    assert handler.parse_ports("80,443") == [80, 443]
    assert handler.parse_ports("80-82,90") == [80, 81, 82, 90]

@patch('server.web.handler.get.network.ModbusScanHandler.scan_ports')
@patch('server.web.handler.get.network.ModbusScanHandler.scan_ip')
def test_modbus_scan(mock_scan_ip, mock_scan_ports):
    handler = ModbusScanHandler()

    ports = "502"
    assert handler.parse_ports(ports) == [502]

    ports = "502,503-510,1502"
    parsed_ports = handler.parse_ports(ports)
    assert parsed_ports == [502, 503, 504, 505, 506, 507, 508, 509, 510, 1502]
    

    # Mock the scan_ip method to return False
    mock_scan_ip.return_value = False
    assert handler.scan_ip("localhost", 502, 0.01) == False

    # Mock the scan_ports method to return an empty list
    mock_scan_ports.return_value = []
    assert handler.scan_ports(parsed_ports, 0.001) == []

    # We mock the scan_ports method to return an empty list
    mock_scan_ports.return_value = []
    status_code, response = handler.do_get(RequestData(BlackBoard(), {}, {handler.PORTS: ports}, {}))
    assert status_code == 200
    response = json.loads(response)

    assert handler.DEVICES in response
    assert response[handler.DEVICES] == []

    # Now we mock the scan_ports method to return a list of one device
    mock_scan_ports.return_value = [{handler.IP: "192.168.50.220"}]
    status_code, response = handler.do_get(RequestData(BlackBoard(), {}, {handler.PORTS: ports}, {}))
    assert status_code == 200
    response = json.loads(response)

    assert handler.DEVICES in response
    assert response[handler.DEVICES] == [{handler.IP: "192.168.50.220"}]


