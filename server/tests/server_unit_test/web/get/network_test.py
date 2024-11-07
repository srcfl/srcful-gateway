import pytest
import json
from server.tasks.discoverModbusDevicesTask import DiscoverModbusDevicesTask
from server.web.handler.requestData import RequestData
from server.web.handler.get.network import NetworkHandler
from server.web.handler.get.network import AddressHandler
from server.web.handler.get.modbus_scan import ModbusScanHandler
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

@patch('server.web.handler.get.modbus_scan.NetworkUtils')
def test_modbus_scan(mock_network_utils):
    handler = ModbusScanHandler()
    ports = "502"
    assert NetworkUtils.parse_ports(ports) == [502]
    
    assert NetworkUtils.is_port_open(ip="localhost", port=502, timeout=0.01) == False

    mock_network_utils.get_hosts.return_value = [{NetworkUtils.IP_KEY: "192.168.50.220",
                                                  NetworkUtils.PORT_KEY: 502}]
    
    bb = BlackBoard()

    status_code, response = handler.do_get(RequestData(bb, {}, {NetworkUtils.PORTS_KEY: ports}, {}))
    assert status_code == 200
    
    assert len(bb._tasks) == 1
    assert isinstance(bb._tasks[0], DiscoverModbusDevicesTask)
    
    
def test_parse_address():
    # Test valid IP addresses
    assert NetworkUtils.normalize_ip_url("192.168.1.1") == "http://192.168.1.1"
    assert NetworkUtils.normalize_ip_url("10.0.0.1") == "http://10.0.0.1"
    
    # Test valid URLs with IP addresses
    assert NetworkUtils.normalize_ip_url("http://192.168.1.1") == "http://192.168.1.1"
    assert NetworkUtils.normalize_ip_url("https://192.168.1.1") == "https://192.168.1.1"
    assert NetworkUtils.normalize_ip_url("http://192.168.1.1:8080") == "http://192.168.1.1:8080"
    
    # Test invalid inputs
    assert NetworkUtils.normalize_ip_url("") is None
    assert NetworkUtils.normalize_ip_url("invalid_ip") is None
    assert NetworkUtils.normalize_ip_url("envoy.local") is None
    assert NetworkUtils.normalize_ip_url("256.256.256.256") is None
    assert NetworkUtils.normalize_ip_url("http://google.com") is None  # Hostname instead of IP
    assert NetworkUtils.normalize_ip_url("192.168.1") is None  # Incomplete IP
    
    
def test_extract_ip():
    # Test valid inputs
    assert NetworkUtils.extract_ip("192.168.1.1") == "192.168.1.1"
    assert NetworkUtils.extract_ip("http://192.168.1.1") == "192.168.1.1"
    assert NetworkUtils.extract_ip("https://192.168.1.1") == "192.168.1.1"
    assert NetworkUtils.extract_ip("http://192.168.1.1:8080") == "192.168.1.1"
    
    # Test invalid inputs
    assert NetworkUtils.extract_ip("") is None
    assert NetworkUtils.extract_ip("invalid_ip") is None
    assert NetworkUtils.extract_ip("256.256.256.256") is None
    assert NetworkUtils.extract_ip("http://google.com") is None
    assert NetworkUtils.extract_ip("192.168.1") is None