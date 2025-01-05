import pytest
from unittest.mock import Mock, MagicMock
import json
from server.web.handler.get.modbus import ModbusHandler, ModbusParameter, ReturnType
from server.devices.profile_keys import FunctionCodeKey, DataTypeKey
from server.web.handler.requestData import RequestData

@pytest.fixture
def mock_device():
    device = Mock()
    device.read_registers = Mock(return_value=[500])  # Default read value
    device.write_registers = Mock(return_value=True)  # Default write success
    device.get_SN = Mock(return_value="TEST_DEVICE")
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
    
    mock_request_data.query_params = {
        ModbusParameter.DEVICE_ID: 'test_device',
        ModbusParameter.ADDRESS: '5035',
        ModbusParameter.TYPE: DataTypeKey.U16.value,
        ModbusParameter.SCALE_FACTOR: '0.1'
    }
    
    mock_device.read_registers.return_value = [500]  # Will become 50.0 after scale factor
    
    status, response = handler.do_get(mock_request_data)
    response_data = json.loads(response)
    
    assert status == 200
    assert response_data[ReturnType.REGISTER] == 5035
    assert response_data[ReturnType.SIZE] == 1
    assert response_data[ReturnType.RAW_VALUE] == "01f4"
    assert response_data[ReturnType.VALUE] == 50.0

def test_write_multiple_registers(mock_request_data, mock_device):
    """Test writing multiple registers"""
    mock_request_data.query_params = {
        ModbusParameter.DEVICE_ID: "TEST_DEVICE",
        ModbusParameter.ADDRESS: "1000",
        ModbusParameter.FUNCTION_CODE: str(FunctionCodeKey.WRITE_MULTIPLE_REGISTERS.value),
        ModbusParameter.VALUES: "10,20,30"
    }
    
    handler = ModbusHandler()
    status, response = handler.do_get(mock_request_data)
    
    assert status == 200
    data = json.loads(response)
    assert data["address"] == 1000
    assert data["success"] is True
    assert data["values"] == [10, 20, 30]
    mock_device.write_registers.assert_called_once_with(1000, [10, 20, 30])

def test_write_without_values(mock_request_data):
    """Test write operation without values parameter"""
    mock_request_data.query_params = {
        ModbusParameter.DEVICE_ID: "TEST_DEVICE",
        ModbusParameter.ADDRESS: "1000",
        ModbusParameter.FUNCTION_CODE: str(FunctionCodeKey.WRITE_MULTIPLE_REGISTERS.value)
    }
    
    handler = ModbusHandler()
    status, response = handler.do_get(mock_request_data)
    
    assert status == 400
    data = json.loads(response)
    assert "error" in data
    assert "missing values" in data["error"].lower()

def test_string_read(mock_request_data, mock_device):
    """Test string register read"""
    handler = ModbusHandler()
    
    mock_request_data.query_params = {
        ModbusParameter.DEVICE_ID: 'test_device',
        ModbusParameter.ADDRESS: '5000',
        ModbusParameter.TYPE: DataTypeKey.STR.value,
        ModbusParameter.SIZE: '3'  # 6 bytes = 3 registers for "Hello"
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
        ModbusParameter.DEVICE_ID: 'test_device',
        ModbusParameter.ADDRESS: '5000',
        ModbusParameter.TYPE: DataTypeKey.F32.value,
        ModbusParameter.SIZE: '2',
        ModbusParameter.SCALE_FACTOR: '1.0'
    }
    
    mock_device.read_registers.return_value = [0x4049, 0x0FDB]  # 3.14159
    
    status, response = handler.do_get(mock_request_data)
    response_data = json.loads(response)
    
    assert status == 200
    assert abs(response_data[ReturnType.VALUE] - 3.14159) < 0.00001

def test_invalid_function_code(mock_request_data):
    """Test with invalid function code"""
    mock_request_data.query_params = {
        ModbusParameter.DEVICE_ID: "TEST_DEVICE",
        ModbusParameter.ADDRESS: "1000",
        ModbusParameter.FUNCTION_CODE: "99"  # Valid number but invalid function code
    }
    
    handler = ModbusHandler()
    status, response = handler.do_get(mock_request_data)
    
    assert status == 400
    data = json.loads(response)
    assert "error" in data
    assert "invalid function code: 99" in data["error"]

def test_non_numeric_function_code(mock_request_data):
    """Test with non-numeric function code"""
    mock_request_data.query_params = {
        ModbusParameter.DEVICE_ID: "TEST_DEVICE",
        ModbusParameter.ADDRESS: "1000",
        ModbusParameter.FUNCTION_CODE: "abc"  # Non-numeric value
    }
    
    handler = ModbusHandler()
    status, response = handler.do_get(mock_request_data)
    
    assert status == 400
    data = json.loads(response)
    assert "error" in data
    assert "function code must be a number" in data["error"]

def test_missing_device_id(mock_request_data):
    """Test without device_id parameter"""
    mock_request_data.query_params = {
        ModbusParameter.ADDRESS: "1000",
        ModbusParameter.FUNCTION_CODE: str(FunctionCodeKey.READ_HOLDING_REGISTERS.value)
    }
    
    handler = ModbusHandler()
    status, response = handler.do_get(mock_request_data)
    
    assert status == 400
    data = json.loads(response)
    assert "error" in data
    assert "missing device" in data["error"].lower()

def test_missing_address(mock_request_data):
    """Test without address parameter"""
    mock_request_data.query_params = {
        ModbusParameter.DEVICE_ID: "TEST_DEVICE",
        ModbusParameter.FUNCTION_CODE: str(FunctionCodeKey.READ_HOLDING_REGISTERS.value)
    }
    
    handler = ModbusHandler()
    status, response = handler.do_get(mock_request_data)
    
    assert status == 400
    data = json.loads(response)
    assert "error" in data
    assert "missing address" in data["error"].lower()

def test_device_not_found(mock_request_data):
    """Test with non-existent device"""
    mock_request_data.bb.devices.find_sn.return_value = None
    mock_request_data.query_params = {
        ModbusParameter.DEVICE_ID: "NONEXISTENT",
        ModbusParameter.ADDRESS: "1000",
        ModbusParameter.FUNCTION_CODE: str(FunctionCodeKey.READ_HOLDING_REGISTERS.value)
    }
    
    handler = ModbusHandler()
    status, response = handler.do_get(mock_request_data)
    
    assert status == 400
    data = json.loads(response)
    assert "error" in data
    assert "device not found" in data["error"].lower()

def test_write_invalid_values_format(mock_request_data):
    """Test write with invalid values format"""
    mock_request_data.query_params = {
        ModbusParameter.DEVICE_ID: "TEST_DEVICE",
        ModbusParameter.ADDRESS: "1000",
        ModbusParameter.FUNCTION_CODE: str(FunctionCodeKey.WRITE_MULTIPLE_REGISTERS.value),
        ModbusParameter.VALUES: "10,abc,30"  # Invalid value format
    }
    
    handler = ModbusHandler()
    status, response = handler.do_get(mock_request_data)
    
    assert status == 400
    data = json.loads(response)
    assert "error" in data
    assert "invalid values format" in data["error"].lower()

def test_write_failure(mock_request_data, mock_device):
    """Test write operation when device returns failure"""
    mock_device.write_registers.return_value = False
    mock_request_data.query_params = {
        ModbusParameter.DEVICE_ID: "TEST_DEVICE",
        ModbusParameter.ADDRESS: "1000",
        ModbusParameter.FUNCTION_CODE: str(FunctionCodeKey.WRITE_MULTIPLE_REGISTERS.value),
        ModbusParameter.VALUES: "10,20,30"
    }
    
    handler = ModbusHandler()
    status, response = handler.do_get(mock_request_data)
    
    assert status == 200  # Still returns 200 as the request was valid
    data = json.loads(response)
    assert data["success"] is False