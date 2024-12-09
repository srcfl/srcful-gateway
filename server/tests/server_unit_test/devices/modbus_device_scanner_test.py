import pytest
from unittest.mock import patch, MagicMock
from server.devices.inverters.modbus_device_scanner import scan_for_modbus_devices
from server.devices.inverters.ModbusTCP import ModbusTCP
from server.devices.supported_devices.profiles import ModbusProfile, RegisterInterval
from server.devices.profile_keys import ProtocolKey

@pytest.fixture
def mock_modbus_device():
    mock_device = MagicMock(spec=ModbusTCP)
    mock_device.ip = "192.168.1.100"
    mock_device.port = 502
    mock_device.mac = "00:11:22:33:44:55"
    mock_device.device_type = "Test Inverter"
    mock_device.connect.return_value = True
    mock_device.read_registers.return_value = [5000]  # Simulating 50Hz reading
    return mock_device

@pytest.fixture
def mock_profile():
    profile = MagicMock(spec=ModbusProfile)
    profile.protocol = ProtocolKey.MODBUS
    profile.name = "Test Inverter"
    profile.registers = [
        RegisterInterval(
            operation="read",
            start_register=0,
            offset=1
        )
    ]
    return profile

@pytest.fixture
def blackboard():
    from server.app.blackboard import BlackBoard
    from server.crypto.crypto_state import CryptoState
    crypto_state = CryptoState()
    return BlackBoard(crypto_state)

@patch('server.devices.inverters.modbus_device_scanner.NetworkUtils.get_hosts')
def test_scan_no_hosts_found(mock_get_hosts):
    """Test scanning when no hosts are found"""
    mock_get_hosts.return_value = []
    devices = scan_for_modbus_devices(ports=[502])
    assert len(devices) == 0

@patch('server.devices.inverters.modbus_device_scanner.ModbusTCP')
@patch('server.devices.inverters.modbus_device_scanner.ModbusDeviceProfiles')
@patch('server.devices.inverters.modbus_device_scanner.NetworkUtils.get_hosts')
def test_scan_finds_single_device(mock_get_hosts, mock_profiles, mock_modbus_class, mock_profile, blackboard):
    """Test scanning finds a single device successfully and saves it to state"""
    # Setup host info
    host_info = MagicMock()
    host_info.ip = "192.168.1.100"
    host_info.port = 502
    host_info.mac = "00:11:22:33:44:55"
    mock_get_hosts.return_value = [host_info]
    
    # Setup profiles
    profiles_instance = MagicMock()
    profiles_instance.get_supported_devices.return_value = [mock_profile]
    mock_profiles.return_value = profiles_instance
    
    # Setup ModbusTCP mock
    mock_device = MagicMock(spec=ModbusTCP)
    mock_device.ip = host_info.ip
    mock_device.port = host_info.port
    mock_device.mac = host_info.mac
    mock_device.device_type = mock_profile.name
    mock_device.connect.return_value = True
    mock_device.read_registers.return_value = [5000]
    mock_device.slave_id = 1
    mock_modbus_class.return_value = mock_device
    
    # Run test
    devices = scan_for_modbus_devices(ports=[502])
    
    # Assertions
    assert len(devices) == 1
    assert devices[0].ip == host_info.ip
    assert devices[0].port == host_info.port
    assert devices[0].device_type == mock_profile.name
    
    # Verify device was saved to state
    blackboard.set_available_devices(devices=devices)
    saved_devices = blackboard.get_available_devices()
    assert len(saved_devices) == 1
    assert saved_devices[0].ip == host_info.ip
    assert saved_devices[0].port == host_info.port
    assert saved_devices[0].device_type == mock_profile.name
    assert saved_devices[0].slave_id == 1