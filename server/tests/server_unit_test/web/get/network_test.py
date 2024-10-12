import pytest
import json
from server.web.handler.requestData import RequestData
from server.web.handler.get.network import NetworkHandler
from server.web.handler.get.network import AddressHandler
from server.web.handler.get.network import ModbusScanHandler
from server.network.wifi import get_connection_configs
from server.blackboard import BlackBoard
from unittest.mock import patch
from server.network.network_utils import NetworkUtils

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
    assert NetworkUtils.parse_ports("80,443") == [80, 443]
    assert NetworkUtils.parse_ports("80-82,90") == [80, 81, 82, 90]

@patch('server.web.handler.get.network.NetworkUtils')
def test_modbus_scan(mock_network_utils):
    handler = ModbusScanHandler()
    ports = "502"
    assert NetworkUtils.parse_ports(ports) == [502]
    
    assert NetworkUtils.is_port_open(ip="localhost", port=502, timeout=0.01) == False

    mock_network_utils.get_hosts.return_value = [{"ip": "192.168.50.220", "port": 502}]

    status_code, response = handler.do_get(RequestData(BlackBoard(), {}, {'ports': ports}, {}))
    assert status_code == 200
    response = json.loads(response)
    assert response[handler.DEVICES] == [{"ip": "192.168.50.220", "port": 502}]