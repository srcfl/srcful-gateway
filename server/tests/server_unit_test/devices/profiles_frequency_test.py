import pytest
from unittest.mock import patch, MagicMock
from server.devices.inverters.ModbusTCP import ModbusTCP
from server.devices.supported_devices.profiles import ModbusProfile, RegisterInterval
from server.devices.profile_keys import ProtocolKey
from server.devices.supported_devices.supported_devices import supported_devices
from server.devices.profile_keys import DeviceCategoryKey, ProfileKey, RegistersKey


FREQUENCY_REGISTER_VALUES = {
    "huawei": [0x1388],  # 5000 = 50.00 Hz
    "solaredge": [0x0000, 0x1388],  # Second register contains frequency
    "sungrow": [0x01F4],  # 500 * 0.1 = 50.0 Hz
    "sma": [0x0000, 0x1388],  # U32: 5000 = 50.00 Hz
    "fronius": [0x4248, 0x0000],  # IEEE-754 float: 50.0
    "deye": [0x1388],  # U32: 5000 = 50.00 Hz
    "deye_micro": [0x1388],  # U16: 5000 = 50.00 Hz
    "growatt": [0x1388],  # 5000 = 50.00 Hz
    "goodwe": [0x1388],  # 5000 = 50.00 Hz
    "ferroamp": [0x4248, 0x0000],  # IEEE-754 float: 50.0
    "sofar": [0x1388],  # 5000 = 50.00 Hz
    "unknown": [0x1388],  # 5000 = 50.00 Hz
}

def get_frequency_test_cases():
    test_cases = []
    for device in supported_devices[DeviceCategoryKey.INVERTERS]:
        freq_register = device[ProfileKey.REGISTERS][0]
        device_name = device[ProfileKey.NAME]
        
        if device_name not in FREQUENCY_REGISTER_VALUES:
            print(f"Warning: No test registers defined for {device_name}")
            continue
            
        test_cases.append({
            "name": device_name,
            "operation": freq_register[RegistersKey.FUNCTION_CODE],
            "start_register": freq_register[RegistersKey.START_REGISTER],
            "num_registers": freq_register[RegistersKey.NUM_OF_REGISTERS],
            "data_type": freq_register[RegistersKey.DATA_TYPE],
            "scale_factor": freq_register[RegistersKey.SCALE_FACTOR],
            "endianess": freq_register[RegistersKey.ENDIANNESS],
            "registers": FREQUENCY_REGISTER_VALUES[device_name],
            "expected_frequency": 50.00,
        })
            
    return test_cases

FREQUENCY_TEST_CASES = get_frequency_test_cases()

@pytest.fixture
def mock_profile_factory():
    def _create_mock_profile(test_case):
        profile = MagicMock(spec=ModbusProfile)
        profile.protocol = ProtocolKey.MODBUS
        profile.name = test_case["name"]
        profile.registers = [
            RegisterInterval(
                function_code=test_case["operation"],
                start_register=test_case["start_register"],
                offset=test_case["num_registers"],
                data_type=test_case["data_type"],
                unit="Hz",
                description="Grid frequency",
                scale_factor=test_case["scale_factor"]
            )
        ]
        return profile
    return _create_mock_profile

@pytest.mark.parametrize("test_case", FREQUENCY_TEST_CASES)
@patch('server.devices.supported_devices.profiles.ModbusDeviceProfiles')
def test_read_frequency(mock_profiles, mock_profile_factory, test_case):
    """Test the _read_frequency method"""
    # Create mock profile for this test case
    mock_profile = mock_profile_factory(test_case)
    
    # Create device instance
    device = ModbusTCP(
        ip="192.168.1.100",
        port=502,
        mac="00:11:22:33:44:55",
        device_type=test_case["name"]
    )
    
    # Setup profile mock
    profiles_instance = MagicMock()
    profiles_instance.get.return_value = mock_profile
    mock_profiles.return_value = profiles_instance
    
    # Mock read_registers to return the specific register values for this profile
    device.read_registers = MagicMock(return_value=test_case["registers"])
    device._get_frequency_register = MagicMock(return_value=mock_profile.registers[0])
    
    # Test frequency reading
    frequency = device._read_frequency()
    
    # Verify results
    assert frequency == test_case["expected_frequency"]
    device.read_registers.assert_called_once_with(
        test_case["operation"],
        test_case["start_register"],
        test_case["num_registers"]
    )
