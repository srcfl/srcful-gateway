import pytest
from unittest.mock import patch, MagicMock
from server.devices.inverters.ModbusTCP import ModbusTCP
from server.devices.supported_devices.profiles import ModbusProfile, RegisterInterval
from server.devices.profile_keys import ProtocolKey, DataType


@pytest.fixture
def mock_huawei_profile():
    profile = MagicMock(spec=ModbusProfile)
    profile.protocol = ProtocolKey.MODBUS
    profile.name = "huawei"
    profile.registers = [
        RegisterInterval(
            operation=0x03,
            start_register=32085,
            offset=1,
            data_type=DataType.U16,
            unit="Hz",
            description="Grid frequency",
            scale_factor=0.01
        )
    ]
    return profile


@patch('server.devices.supported_devices.profiles.ModbusDeviceProfiles')
def test_read_frequency(mock_profiles, mock_huawei_profile):
    """Test the _read_frequency method"""
    # Create device instance
    device = ModbusTCP(
        ip="192.168.1.100",
        port=502,
        mac="00:11:22:33:44:55",
        device_type="huawei"
    )
    
    # Setup profile mock
    profiles_instance = MagicMock()
    profiles_instance.get.return_value = mock_huawei_profile
    mock_profiles.return_value = profiles_instance
    
    # Mock read_registers to return 5000 (50.00 Hz after scale factor)
    device.read_registers = MagicMock(return_value=[5000])
    device._get_frequency_register = MagicMock(return_value=mock_huawei_profile.registers[0])
    
    # Test frequency reading
    frequency = device._read_frequency()
    
    # Verify results
    assert frequency == 50.00
    device.read_registers.assert_called_once_with(0x03, 32085, 1)
