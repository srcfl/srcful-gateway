import pytest
import json
from server.web.handler.requestData import RequestData
from server.web.handler.get.network import NetworkHandler
from server.web.handler.get.network import AddressHandler
from server.web.handler.get.network import ModbusScanHandler
from server.wifi.wifi import get_connection_configs
from server.blackboard import BlackBoard


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
    expected = json.loads(json.dumps({"connections":get_connection_configs()}))   # getConnectionConfigs() returns a list of dicts, so we need to convert it to JSON and back to a dict to compare   
    assert response == expected


def test_network_address(request_data):
    handler = AddressHandler()
    status_code, response = handler.do_get(request_data)
    assert status_code == 200
    response = json.loads(response)
    ip = response["ip"]
    
    assert ip.count(".") == 3
    for part in ip.split("."):
        assert 0 <= int(part) <= 255
    assert response["port"] == 8081

def test_modbus_scan():
    handler = ModbusScanHandler()

    ports = "502"

    assert handler.parse_ports(ports) == [502]

    # status_code, response = handler.do_get(RequestData(BlackBoard(), {}, {"ports": ports}, {}))
    # assert status_code == 200
    # response = json.loads(response)
    # assert isinstance(response, list)
    # assert len(response) > 0