import pytest
from unittest.mock import Mock
from server.devices.registerValue import RegisterValue
from server.devices.profile_keys import DataTypeKey, FunctionCodeKey, EndiannessKey

@pytest.fixture
def mock_device():
    """Fixture providing a mock device with read_registers method"""
    device = Mock()
    # Configure the mock to have read_registers and write_registers methods
    device.read_registers = Mock()
    device.write_registers = Mock(return_value=True)
    return device

def test_u16_value(mock_device):
    """Test unsigned 16-bit integer reading"""
    register = RegisterValue(
        address=1000,
        size=1,
        data_type=DataTypeKey.U16,
        scale_factor=1.0
    )
    
    # Mock device to return 500 (0x01F4)
    mock_device.read_registers.return_value = [500]
    
    raw, swapped, value = register.read_value(mock_device)
    
    assert value == 500
    assert raw.hex() == "01f4"

def test_i16_value(mock_device):
    """Test signed 16-bit integer reading"""
    register = RegisterValue(
        address=1000,
        size=1,
        data_type=DataTypeKey.I16,
        scale_factor=1.0
    )
    
    # Mock device to return -500 (0xFE0C in two's complement)
    mock_device.read_registers.return_value = [0xFE0C]
    
    raw, swapped, value = register.read_value(mock_device)
    
    assert value == -500
    assert raw.hex() == "fe0c"

def test_u32_value(mock_device):
    """Test unsigned 32-bit integer reading"""
    register = RegisterValue(
        address=1000,
        size=2,
        data_type=DataTypeKey.U32,
        scale_factor=1.0
    )
    
    # Mock device to return 70000 (0x00011170)
    mock_device.read_registers.return_value = [0x0001, 0x1170]
    
    raw, swapped, value = register.read_value(mock_device)
    
    assert value == 70000
    assert raw.hex() == "00011170"

def test_i32_value(mock_device):
    """Test signed 32-bit integer reading"""
    register = RegisterValue(
        address=1000,
        size=2,
        data_type=DataTypeKey.I32,
        scale_factor=1.0
    )
    
    # Mock device to return -70000 (0xFFFEEE90 in two's complement)
    mock_device.read_registers.return_value = [0xFFFE, 0xEE90]
    
    raw, swapped, value = register.read_value(mock_device)
    
    assert value == -70000
    assert raw.hex() == "fffeee90"

def test_f32_value(mock_device):
    """Test 32-bit float reading"""
    register = RegisterValue(
        address=1000,
        size=2,
        data_type=DataTypeKey.F32,
        scale_factor=1.0
    )
    
    # Mock device to return 3.14159 (0x40490FDB)
    mock_device.read_registers.return_value = [0x4049, 0x0FDB]
    
    raw, swapped, value = register.read_value(mock_device)
    
    assert abs(value - 3.14159) < 0.00001
    assert raw.hex() == "40490fdb"

def test_str_value(mock_device):
    """Test string reading"""
    register = RegisterValue(
        address=1000,
        size=3,  # 6 bytes = 3 registers
        data_type=DataTypeKey.STR,
        scale_factor=1.0
    )
    
    # Mock device to return "Hello" (0x48656C6C6F00)
    mock_device.read_registers.return_value = [0x4865, 0x6C6C, 0x6F00]
    
    raw, swapped, value = register.read_value(mock_device)
    
    assert value == "Hello"
    assert raw.hex() == "48656c6c6f00"

def test_scale_factor(mock_device):
    """Test scale factor application"""
    register = RegisterValue(
        address=1000,
        size=1,
        data_type=DataTypeKey.U16,
        scale_factor=0.1
    )
    
    # Mock device to return 500
    mock_device.read_registers.return_value = [500]
    
    raw, swapped, value = register.read_value(mock_device)
    
    assert value == 50.0  # 500 * 0.1
    assert raw.hex() == "01f4"

def test_no_scale_factor_for_string(mock_device):
    """Test that scale factor is not applied to strings"""
    register = RegisterValue(
        address=1000,
        size=3,
        data_type=DataTypeKey.STR,
        scale_factor=0.1
    )
    
    # Mock device to return "500"
    mock_device.read_registers.return_value = [0x3530, 0x3000, 0x0000]
    
    raw, swapped, value = register.read_value(mock_device)
    
    assert value == "500"  # Should not be scaled
    assert raw.hex() == "353030000000"

def test_invalid_read(mock_device):
    """Test handling of invalid reads"""
    register = RegisterValue(
        address=1000,
        size=1,
        data_type=DataTypeKey.U16
    )
    
    # Mock device to return None
    mock_device.read_registers.return_value = None
    
    raw, swapped, value = register.read_value(mock_device)
    
    assert value is None
    assert raw == bytearray()

def test_read_registers_called_correctly(mock_device):
    """Test that read_registers is called with correct parameters"""
    register = RegisterValue(
        address=1000,
        size=2,
        function_code=FunctionCodeKey.READ_HOLDING_REGISTERS,
        data_type=DataTypeKey.U32
    )
    
    mock_device.read_registers.return_value = [0, 0]
    register.read_value(mock_device)
    
    mock_device.read_registers.assert_called_once_with(
        FunctionCodeKey.READ_HOLDING_REGISTERS,
        1000,  # address
        2      # size
    )

def test_error_handling(mock_device):
    """Test error handling when interpreting values"""
    register = RegisterValue(
        address=1000,
        size=1,
        data_type=DataTypeKey.F32  # Intentionally wrong size for F32
    )
    
    mock_device.read_registers.return_value = [0x1234]  # Not enough data for F32
    
    raw, swapped, value = register.read_value(mock_device)
    
    assert value is None  # Should return None on error
    assert raw.hex() == "1234"

def test_numeric_not_treated_as_string(mock_device):
    """Test that numeric values aren't accidentally treated as strings"""
    register = RegisterValue(
        address=5035,
        size=1,
        data_type=DataTypeKey.U16,  # Make sure we're using the right data type
        scale_factor=0.1
    )
    
    # Mock device to return 500 (0x01F4)
    mock_device.read_registers.return_value = [500]
    
    raw, swapped, value = register.read_value(mock_device)
    
    assert isinstance(value, (int, float))  # Verify the type is numeric
    assert value == 50.0  # 500 * 0.1
    assert raw.hex() == "01f4"
    assert not isinstance(value, str)  # Explicitly verify it's not a string

def test_data_type_handling(mock_device):
    """Test that data types are correctly passed and handled"""
    test_cases = [
        (DataTypeKey.U16, [500], 500),
        (DataTypeKey.I16, [0xFE0C], -500),
        (DataTypeKey.U32, [0x0001, 0x1170], 70000),
        (DataTypeKey.I32, [0xFFFE, 0xEE90], -70000),
        (DataTypeKey.F32, [0x4049, 0x0FDB], 3.14159),
        (DataTypeKey.STR, [0x4865, 0x6C6C, 0x6F00], "Hello"),
    ]
    
    for data_type, register_values, expected_value in test_cases:
        register = RegisterValue(
            address=1000,
            size=len(register_values),
            data_type=data_type,
            scale_factor=1.0
        )
        
        mock_device.read_registers.return_value = register_values
        raw, swapped, value = register.read_value(mock_device)
        
        assert value is not None, f"Value should not be None for data type {data_type}"
        if data_type == DataTypeKey.F32:
            assert abs(value - expected_value) < 0.00001, f"Failed for data type {data_type}"
        else:
            assert value == expected_value, f"Failed for data type {data_type}"
            
def test_invalid_data_type(mock_device):
    """Test handling of invalid data type"""
    register = RegisterValue(
        address=1000,
        size=1,
        data_type="INVALID_TYPE",  # Invalid data type
        scale_factor=1.0
    )
    
    mock_device.read_registers.return_value = [500]
    raw, swapped, value = register.read_value(mock_device)
    
    assert value is None, "Invalid data type should return None"

def test_u32_endianness(mock_device):
    """Test U32 value with different endianness settings"""
    # Test big-endian (default)
    register_be = RegisterValue(
        address=1000,
        size=2,
        data_type=DataTypeKey.U32,
        scale_factor=1.0,
        endianness=EndiannessKey.BIG
    )
    
    # Value 0x12345678 (305419896 in decimal)
    mock_device.read_registers.return_value = [0x1234, 0x5678]
    raw, swapped, value = register_be.read_value(mock_device)
    assert value == 305419896  # 0x12345678
    assert raw.hex() == "12345678"
    assert swapped.hex() == "12345678"
    
    # Test little-endian
    register_le = RegisterValue(
        address=1000,
        size=2,
        data_type=DataTypeKey.U32,
        scale_factor=1.0,
        endianness=EndiannessKey.LITTLE
    )
    
    # Same registers but interpreted as little-endian
    # When registers [0x1234, 0x5678] are interpreted in little-endian:
    # - Register order is swapped: [0x5678, 0x1234]
    # - Bytes within registers stay big-endian
    # - Final value: 0x56781234 (1450709556 in decimal)
    
    raw, swapped, value = register_le.read_value(mock_device)
    assert value == 1450709556  # 0x56781234
    assert raw.hex() == "12345678"  # Raw bytes stay the same, just interpreted differently
    assert swapped.hex() == "56781234"

def test_f32_endianness(mock_device):
    """Test F32 value with different endianness settings"""
    # Test big-endian (default)
    register_be = RegisterValue(
        address=1000,
        size=2,
        data_type=DataTypeKey.F32,
        scale_factor=1.0,
        endianness=EndiannessKey.BIG
    )
    
    # Value ~3.14159 (0x40490FDB)
    mock_device.read_registers.return_value = [0x4049, 0x0FDB]
    raw, swapped, value = register_be.read_value(mock_device)
    assert abs(value - 3.14159) < 0.001
    assert raw.hex() == "40490fdb"
    assert swapped.hex() == "40490fdb"
    
    # Test little-endian
    register_le = RegisterValue(
        address=1000,
        size=2,
        data_type=DataTypeKey.F32,
        scale_factor=1.0,
        endianness=EndiannessKey.LITTLE
    )
    
    # Same value but registers swapped for little-endian
    raw, swapped, value = register_le.read_value(mock_device)
    # assert abs(value - 2.16198) < 0.001
    assert raw.hex() == "40490fdb"
    assert swapped.hex() == "0fdb4049"

def test_str_endianness(mock_device):
    """Test string value with different endianness settings"""
    # Test big-endian (default)
    register_be = RegisterValue(
        address=1000,
        size=3,
        data_type=DataTypeKey.STR,
        scale_factor=1.0,
        endianness=EndiannessKey.BIG
    )
    
    # String "Hello" in big-endian
    mock_device.read_registers.return_value = [0x4865, 0x6C6C, 0x6F00]  # "He" "ll" "o\0"
    raw, swapped, value = register_be.read_value(mock_device)
    assert value == "Hello"
    assert raw.hex() == "48656c6c6f00"  # Raw bytes in original memory order
    assert swapped.hex() == "48656c6c6f00"  # For big-endian, swapped is same as raw
    
    # Test little-endian
    register_le = RegisterValue(
        address=1000,
        size=3,
        data_type=DataTypeKey.STR,
        scale_factor=1.0,
        endianness=EndiannessKey.LITTLE
    )
    
    # For little-endian:
    # - raw shows original memory order
    # - swapped shows register-swapped order
    # - value is interpreted from swapped bytes
    mock_device.read_registers.return_value = [0x4865, 0x6C6C, 0x6F00]
    raw, swapped, value = register_le.read_value(mock_device)
    assert value == "o\x00llHe"  # Value interpreted from swapped bytes
    assert raw.hex() == "48656c6c6f00"  # Raw bytes in original memory order
    assert swapped.hex() == "6f006c6c4865"  # Bytes after register swapping


def test_write_single_register(mock_device):
    """Test writing a single register value"""
    # Write value 500 to register 1000
    success = RegisterValue.write_single(mock_device, address=1000, value=500)
    
    assert success is True
    mock_device.write_registers.assert_called_once_with(1000, [500])

def test_write_single_register_truncation(mock_device):
    """Test that values are properly truncated to 16 bits"""
    # Write value 0x12345678, should be truncated to 0x5678
    success = RegisterValue.write_single(mock_device, address=1000, value=0x12345678)
    
    assert success is True
    mock_device.write_registers.assert_called_once_with(1000, [0x5678])

def test_write_multiple_registers(mock_device):
    """Test writing multiple register values"""
    values = [10, 20, 30]
    success = RegisterValue.write_multiple(mock_device, address=1000, values=values)
    
    assert success is True
    mock_device.write_registers.assert_called_once_with(1000, [10, 20, 30])

def test_write_multiple_registers_truncation(mock_device):
    """Test that multiple values are properly truncated to 16 bits"""
    values = [0x12345678, 0xFFFFFFFF, 0x0000FFFF]
    success = RegisterValue.write_multiple(mock_device, address=1000, values=values)
    
    assert success is True
    mock_device.write_registers.assert_called_once_with(1000, [0x5678, 0xFFFF, 0xFFFF])

def test_write_single_register_device_error(mock_device):
    """Test handling of device errors during single register write"""
    mock_device.write_registers.return_value = False
    success = RegisterValue.write_single(mock_device, address=1000, value=500)
    
    assert success is False
    mock_device.write_registers.assert_called_once_with(1000, [500])

def test_write_multiple_registers_device_error(mock_device):
    """Test handling of device errors during multiple register write"""
    mock_device.write_registers.return_value = False
    success = RegisterValue.write_multiple(mock_device, address=1000, values=[10, 20, 30])
    
    assert success is False
    mock_device.write_registers.assert_called_once_with(1000, [10, 20, 30])

def test_write_single_register_no_write_support(mock_device):
    """Test handling of devices that don't support writing"""
    # Remove write_registers method
    delattr(mock_device, 'write_registers')
    
    success = RegisterValue.write_single(mock_device, address=1000, value=500)
    assert success is False

def test_write_multiple_registers_no_write_support(mock_device):
    """Test handling of devices that don't support writing"""
    # Remove write_registers method
    delattr(mock_device, 'write_registers')
    
    success = RegisterValue.write_multiple(mock_device, address=1000, values=[10, 20, 30])
    assert success is False

def test_write_single_register_exception(mock_device):
    """Test handling of exceptions during single register write"""
    mock_device.write_registers.side_effect = Exception("Test error")
    
    success = RegisterValue.write_single(mock_device, address=1000, value=500)
    assert success is False

def test_write_multiple_registers_exception(mock_device):
    """Test handling of exceptions during multiple register write"""
    mock_device.write_registers.side_effect = Exception("Test error")
    
    success = RegisterValue.write_multiple(mock_device, address=1000, values=[10, 20, 30])
    assert success is False
