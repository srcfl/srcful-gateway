import pytest
from unittest.mock import Mock
import json
from server.web.handler.get.modbus import ModbusHandler, RegisterType, ReturnType
from server.web.handler.requestData import RequestData

@pytest.fixture
def mock_device():
    device = Mock()
    device.read_registers = Mock()
    device.get_config = Mock(return_value={'some': 'config'})
    return device

@pytest.fixture
def mock_request_data(mock_device):
    request = Mock(spec=RequestData)
    request.query_params = {}
    request.bb = Mock()
    request.bb.devices = Mock()
    request.bb.devices.lst = [mock_device]
    request.bb.devices.find_sn = Mock(return_value=mock_device)
    return request

def test_basic_u16_read(mock_request_data, mock_device):
    """Test basic U16 register read with minimal parameters"""
    handler = ModbusHandler()
    
    # Setup mock request
    mock_request_data.query_params = {
        RegisterType.DEVICE_ID: 'test_device',
        RegisterType.ADDRESS: '5035',
        RegisterType.TYPE: 'U16',
        RegisterType.SCALE_FACTOR: '0.1'
    }
    
    # Setup mock device response
    mock_device.read_registers.return_value = [500]  # Will become 50.0 after scale factor
    
    # Execute request
    status, response = handler.do_get(mock_request_data)
    response_data = json.loads(response)
    
    # Verify response
    assert status == 200
    assert response_data[ReturnType.REGISTER] == 5035
    assert response_data[ReturnType.SIZE] == 1
    assert response_data[ReturnType.RAW_VALUE] == "01f4"
    assert response_data[ReturnType.VALUE] == 50.0

def test_string_read(mock_request_data, mock_device):
    """Test string register read"""
    handler = ModbusHandler()
    
    mock_request_data.query_params = {
        RegisterType.DEVICE_ID: 'test_device',
        RegisterType.ADDRESS: '5000',
        RegisterType.TYPE: 'STR',
        RegisterType.SIZE: '3'  # 6 bytes = 3 registers for "Hello"
    }
    
    mock_device.read_registers.return_value = [0x4865, 0x6C6C, 0x6F00]  # "Hello"
    
    status, response = handler.do_get(mock_request_data)
    response_data = json.loads(response)
    
    assert status == 200
    assert response_data[ReturnType.VALUE] == "Hello"
    assert response_data[ReturnType.RAW_VALUE] == "48656c6c6f00"

def test_f32_read(mock_request_data, mock_device):
    """Test F32 register read"""
    handler = ModbusHandler()
    
    mock_request_data.query_params = {
        RegisterType.DEVICE_ID: 'test_device',
        RegisterType.ADDRESS: '5000',
        RegisterType.TYPE: 'F32',
        RegisterType.SIZE: '2',
        RegisterType.SCALE_FACTOR: '1.0'
    }
    
    mock_device.read_registers.return_value = [0x4049, 0x0FDB]  # 3.14159
    
    status, response = handler.do_get(mock_request_data)
    response_data = json.loads(response)
    
    assert status == 200
    assert abs(response_data[ReturnType.VALUE] - 3.14159) < 0.00001

def test_missing_device_id(mock_request_data):
    """Test error handling for missing device ID"""
    handler = ModbusHandler()
    
    mock_request_data.query_params = {
        RegisterType.ADDRESS: '5000'
    }
    
    status, response = handler.do_get(mock_request_data)
    response_data = json.loads(response)
    
    assert status == 400
    assert "missing device index" in response_data["error"]

def test_missing_address(mock_request_data):
    """Test error handling for missing address"""
    handler = ModbusHandler()
    
    mock_request_data.query_params = {
        RegisterType.DEVICE_ID: 'test_device'
    }
    
    status, response = handler.do_get(mock_request_data)
    response_data = json.loads(response)
    
    assert status == 400
    assert "missing address" in response_data["error"]

def test_device_not_found(mock_request_data):
    """Test error handling for device not found"""
    handler = ModbusHandler()
    
    mock_request_data.query_params = {
        RegisterType.DEVICE_ID: 'test_device',
        RegisterType.ADDRESS: '5000'
    }
    mock_request_data.bb.devices.find_sn.return_value = None
    
    status, response = handler.do_get(mock_request_data)
    response_data = json.loads(response)
    
    assert status == 400
    assert "device not found" in response_data["error"]