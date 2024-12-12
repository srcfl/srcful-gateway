import pytest
from unittest.mock import MagicMock
from server.devices.registerValue import RegisterValue
from server.devices.profile_keys import DataTypeKey


@pytest.fixture
def mock_device():
    device = MagicMock()
    # Mock the read_registers method to return predefined values
    device.read_registers.return_value = [0x1234, 0x5678]  # Two 16-bit registers
    return device


def test_u16_register():
    """Test unsigned 16-bit integer reading"""
    device = MagicMock()
    device.read_registers.return_value = [0x1234]  # 4660 in decimal
    
    reg = RegisterValue(
        address=0,
        size=1,
        function_code=0x03,
        data_type=DataTypeKey.U16,
        scale_factor=1.0
    )
    
    raw, value = reg.read_value(device)
    assert value == 4660
    assert raw == bytes([0x12, 0x34])


def test_i16_register():
    """Test signed 16-bit integer reading"""
    device = MagicMock()
    device.read_registers.return_value = [0xFFF0]  # -16 in 16-bit signed
    
    reg = RegisterValue(
        address=0,
        size=1,
        function_code=0x03,
        data_type=DataTypeKey.I16,
        scale_factor=1.0
    )
    
    raw, value = reg.read_value(device)
    assert value == -16
    assert raw == bytes([0xFF, 0xF0])


def test_u32_register():
    """Test unsigned 32-bit integer reading"""
    device = MagicMock()
    device.read_registers.return_value = [0x1234, 0x5678]  # 305419896 in decimal
    
    reg = RegisterValue(
        address=0,
        size=2,
        function_code=0x03,
        data_type=DataTypeKey.U32,
        scale_factor=1.0
    )
    
    raw, value = reg.read_value(device)
    assert value == 305419896
    assert raw == bytes([0x12, 0x34, 0x56, 0x78])


def test_i32_register():
    """Test signed 32-bit integer reading"""
    device = MagicMock()
    device.read_registers.return_value = [0xFFFF, 0xFFF0]  # -16 in 32-bit signed
    
    reg = RegisterValue(
        address=0,
        size=2,
        function_code=0x03,
        data_type=DataTypeKey.I32,
        scale_factor=1.0
    )
    
    raw, value = reg.read_value(device)
    assert value == -16
    assert raw == bytes([0xFF, 0xFF, 0xFF, 0xF0])


def test_f32_register():
    """Test 32-bit float reading"""
    device = MagicMock()
    # These values represent float 123.456 in ABCD format (big endian)
    device.read_registers.return_value = [0x42F6, 0xE979]
    
    reg = RegisterValue(
        address=0,
        size=2,
        function_code=0x03,
        data_type=DataTypeKey.F32,
        scale_factor=1.0
    )
    
    raw, value = reg.read_value(device)
    assert abs(value - 123.456) < 0.001  # Compare with tolerance
    assert raw == bytes([0x42, 0xF6, 0xE9, 0x79])


def test_string_register():
    """Test string reading"""
    device = MagicMock()
    # ASCII values for "Hello"
    device.read_registers.return_value = [0x4865, 0x6C6C, 0x6F00]
    
    reg = RegisterValue(
        address=0,
        size=3,
        function_code=0x03,
        data_type=DataTypeKey.STR,
        scale_factor=1.0
    )
    
    raw, value = reg.read_value(device)
    assert value == "Hello"
    assert raw == bytes([0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x00])


def test_scale_factor():
    """Test scale factor application"""
    device = MagicMock()
    device.read_registers.return_value = [0x1234]  # 4660 in decimal
    
    reg = RegisterValue(
        address=0,
        size=1,
        function_code=0x03,
        data_type=DataTypeKey.U16,
        scale_factor=0.1
    )
    
    raw, value = reg.read_value(device)
    assert value == 466.0  # 4660 * 0.1
    assert raw == bytes([0x12, 0x34])


def test_function_codes():
    """Test different function codes"""
    device = MagicMock()
    device.read_registers.return_value = [0x1234]
    
    # Test holding registers (0x03)
    reg = RegisterValue(
        address=0,
        size=1,
        function_code=0x03,
        data_type=DataTypeKey.U16
    )
    reg.read_value(device)
    device.read_registers.assert_called_with(0x03, 0, 1)
    
    # Test input registers (0x04)
    reg = RegisterValue(
        address=0,
        size=1,
        function_code=0x04,
        data_type=DataTypeKey.U16
    )
    reg.read_value(device)
    device.read_registers.assert_called_with(0x04, 0, 1)