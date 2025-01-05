
import json
import pytest
from unittest.mock import Mock
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.web.handler.get.device import Handler
from server.web.handler.requestData import RequestData
from server.devices.ICom import ICom
import server.tests.config_defaults as config_defaults


@pytest.fixture
def handler():
    return Handler()

@pytest.fixture
def mock_device():

    def create_device():
        device = Mock(spec=ICom)
        device.get_config.return_value = (config_defaults.P1_TELNET_CONFIG.copy())
        device.get_SN.return_value = config_defaults.P1_TELNET_CONFIG["meter_serial_number"]
        device.get_name.return_value = "Test Device"
        device.get_client_name.return_value = "device.test"
        device.client = None
        return device
    
    device = create_device()
    return device
    

@pytest.fixture
def blackboard():
    bb = BlackBoard(Mock(spec=CryptoState))
    return bb

@pytest.fixture
def request_data(blackboard):
    return RequestData(blackboard, {}, {}, {})

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
    assert result[0]["is_open"] == True
    assert result[0]["id"] == "abc5qwerty"
    assert result[0]["connection"]["connection"] == "P1Telnet"
    assert result[0]["connection"]["ip"] == "localhost"

def test_single_device_in_settings(handler, request_data, mock_device):
    """Test handler returns correct data for a single open device"""
    mock_device.is_open.return_value = True
    request_data.bb.settings.devices.connections.append(mock_device.get_config())
    
    status, response = handler.do_get(request_data)
    result = json.loads(response)
    
    assert status == 200
    assert len(result) == 1
    assert result[0]["is_open"] == False
    assert result[0]["id"] == "abc5qwerty"
    assert result[0]["connection"]["connection"] == "P1Telnet"
    assert result[0]["connection"]["ip"] == "localhost"

def test_single_device(handler, request_data, mock_device):
    """Test handler returns correct data for a single open device"""
    mock_device.is_open.return_value = True
    request_data.bb.devices.lst = [mock_device]
    request_data.bb.settings.devices.connections.append(mock_device.get_config().copy())
    
    status, response = handler.do_get(request_data)
    result = json.loads(response)
    
    assert status == 200
    assert len(result) == 1
    assert result[0]["is_open"] == True
    assert result[0]["id"] == "abc5qwerty"
    assert result[0]["connection"]["connection"] == "P1Telnet"
    assert result[0]["connection"]["ip"] == "localhost"

def test_single_closed_device(handler, request_data, mock_device):
    """Test handler returns correct data for a single closed device"""
    mock_device.is_open.return_value = False
    request_data.bb.devices.lst = [mock_device]
    
    status, response = handler.do_get(request_data)
    result = json.loads(response)
    
    assert status == 200
    assert len(result) == 1
    assert result[0]["is_open"] == False
    assert result[0]["id"] ==  "abc5qwerty"

def test_multiple_devices(handler, request_data, mock_device):
    """Test handler returns correct data for multiple devices"""
    # First device (open)
    device1 = Mock(spec=ICom)
    device1.get_config.return_value = {"connection": "TCP", "ip": "192.168.1.100"}
    device1.is_open.return_value = True
    device1.get_SN.return_value = "DEV1"
    device1.get_name.return_value = "Test Device 1"
    device1.get_client_name.return_value = "device.test.1"
    # Second device (closed)
    device2 = Mock(spec=ICom)
    device2.get_config.return_value = {"connection": "RTU", "port": "/dev/ttyUSB0"}
    device2.is_open.return_value = False
    device2.get_SN.return_value = "DEV2"
    device2.get_name.return_value = "Test Device 2"
    device2.get_client_name.return_value = "device.test.2"
    request_data.bb.devices.lst = [device1, device2]
    
    status, response = handler.do_get(request_data)
    result = json.loads(response)
    
    assert status == 200
    assert len(result) == 2
    
    # Check first device
    assert result[0]["is_open"] == True
    assert result[0]["id"] == "DEV1"
    assert result[0]["connection"]["connection"] == "TCP"
    
    # Check second device
    assert result[1]["is_open"] == False
    assert result[1]["id"] == "DEV2"
    assert result[1]["connection"]["connection"] == "RTU"
