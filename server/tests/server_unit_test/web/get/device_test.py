
import json
import pytest
from unittest.mock import Mock, patch
from server.app.blackboard import BlackBoard
from server.web.handler.get.device import Handler
from server.web.handler.requestData import RequestData
from server.devices.ICom import ICom

@pytest.fixture
def handler():
    return Handler()

@pytest.fixture
def mock_device():

    def create_device():
        device = Mock(spec=ICom)
        device.get_config.return_value = ({
            "connection": "TCP",
            "ip": "192.168.1.100",
            "port": 502,
            "mac": "TEST123"
        }.copy())
        device.get_SN.return_value = "TEST123"
        return device
    
    device = create_device()
    return device
    

@pytest.fixture
def mock_blackboard():
    bb = Mock(spec=BlackBoard)
    bb.devices = Mock()
    bb.devices.lst = []
    bb.settings = Mock()
    bb.settings.devices = Mock()
    bb.settings.devices.connections = []
    return bb

@pytest.fixture
def request_data(mock_blackboard):
    return RequestData(mock_blackboard, {}, {}, {})

def test_schema(handler):
    """Test that schema returns the expected structure"""
    schema = handler.schema()
    assert schema["type"] == "get"
    assert "description" in schema
    assert "returns" in schema
    assert isinstance(schema["returns"], list)

def test_empty_device_list(handler, request_data):
    """Test handler returns empty list when no devices"""
    status, response = handler.do_get(request_data)
    
    assert status == 200
    assert json.loads(response) == []

def test_single_open_device(handler, request_data, mock_device):
    """Test handler returns correct data for a single open device"""
    mock_device.is_open.return_value = True
    request_data.bb.devices.lst = [mock_device]
    
    status, response = handler.do_get(request_data)
    result = json.loads(response)
    
    assert status == 200
    assert len(result) == 1
    assert result[0]["status"] == "open"
    assert result[0]["id"] == "TEST123"
    assert result[0]["connection"] == "TCP"
    assert result[0]["ip"] == "192.168.1.100"
    assert result[0]["port"] == 502

def test_single_device_in_settings(handler, request_data, mock_device):
    """Test handler returns correct data for a single open device"""
    mock_device.is_open.return_value = True
    request_data.bb.settings.devices.connections.append(mock_device.get_config())
    
    status, response = handler.do_get(request_data)
    result = json.loads(response)
    
    assert status == 200
    assert len(result) == 1
    assert result[0]["status"] == "pending"
    assert result[0]["id"] == "TEST123"
    assert result[0]["connection"] == "TCP"
    assert result[0]["ip"] == "192.168.1.100"
    assert result[0]["port"] == 502

def test_single_device(handler, request_data, mock_device):
    """Test handler returns correct data for a single open device"""
    mock_device.is_open.return_value = True
    request_data.bb.devices.lst = [mock_device]
    request_data.bb.settings.devices.connections.append(mock_device.get_config().copy())
    
    status, response = handler.do_get(request_data)
    result = json.loads(response)
    
    assert status == 200
    assert len(result) == 1
    assert result[0]["status"] == "open"
    assert result[0]["id"] == "TEST123"
    assert result[0]["connection"] == "TCP"
    assert result[0]["ip"] == "192.168.1.100"
    assert result[0]["port"] == 502

def test_single_closed_device(handler, request_data, mock_device):
    """Test handler returns correct data for a single closed device"""
    mock_device.is_open.return_value = False
    request_data.bb.devices.lst = [mock_device]
    
    status, response = handler.do_get(request_data)
    result = json.loads(response)
    
    assert status == 200
    assert len(result) == 1
    assert result[0]["status"] == "closed"
    assert result[0]["id"] == "TEST123"

def test_multiple_devices(handler, request_data, mock_device):
    """Test handler returns correct data for multiple devices"""
    # First device (open)
    device1 = Mock(spec=ICom)
    device1.get_config.return_value = {"connection": "TCP", "ip": "192.168.1.100"}
    device1.is_open.return_value = True
    device1.get_SN.return_value = "DEV1"
    
    # Second device (closed)
    device2 = Mock(spec=ICom)
    device2.get_config.return_value = {"connection": "RTU", "port": "/dev/ttyUSB0"}
    device2.is_open.return_value = False
    device2.get_SN.return_value = "DEV2"
    
    request_data.bb.devices.lst = [device1, device2]
    
    status, response = handler.do_get(request_data)
    result = json.loads(response)
    
    assert status == 200
    assert len(result) == 2
    
    # Check first device
    assert result[0]["status"] == "open"
    assert result[0]["id"] == "DEV1"
    assert result[0]["connection"] == "TCP"
    
    # Check second device
    assert result[1]["status"] == "closed"
    assert result[1]["id"] == "DEV2"
    assert result[1]["connection"] == "RTU"
