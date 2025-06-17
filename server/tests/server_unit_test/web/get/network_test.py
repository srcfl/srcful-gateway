import pytest
import json
from server.crypto.crypto_state import CryptoState
from server.web.handler.requestData import RequestData
from server.web.handler.get.network import NetworkHandler
from server.web.handler.get.network import AddressHandler
from server.network.wifi import get_connection_configs
from server.app.blackboard import BlackBoard
from unittest.mock import Mock
from server.network.network_utils import NetworkUtils


@pytest.fixture
def request_data(blackboard):
    bb = blackboard
    bb.rest_server_port = 8081
    bb.rest_server_ip = "127.0.0.1"
    return RequestData(bb, {}, {}, {})


def test_network(request_data):
    handler = NetworkHandler()
    status_code, response = handler.do_get(request_data)
    assert status_code == 200
    response = json.loads(response)
    expected = json.loads(json.dumps({handler.CONNECTIONS: get_connection_configs()}))   # getConnectionConfigs() returns a list of dicts, so we need to convert it to JSON and back to a dict to compare
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
