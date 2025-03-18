import pytest
from unittest.mock import patch, MagicMock
from server.crypto import crypto
from server.devices.inverters.modbus_device_scanner import scan_for_modbus_devices
from server.devices.inverters.ModbusTCP import ModbusTCP
from server.devices.supported_devices.profiles import ModbusProfile, RegisterInterval
from server.devices.profile_keys import ProtocolKey, DataTypeKey, EndiannessKey
from server.network.network_utils import NetworkUtils
from server.network.network_utils import HostInfo
from server.devices.inverters.modbus_device_scanner import get_profile_by_manufacturer
from server.devices.supported_devices.profiles import ModbusDeviceProfiles
from typing import List

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
def mock_huawei_profile():
    profile = MagicMock(spec=ModbusProfile)
    profile.protocol = ProtocolKey.MODBUS
    profile.name = "huawei"
    profile.registers = [
        RegisterInterval(
            function_code=0x03,
            start_register=0,
            offset=1,
            data_type=DataTypeKey.U16,
            unit="Hz",
            description="Frequency",
            scale_factor=0.01,
            endianness=EndiannessKey.BIG,
        )
    ]
    return profile

@pytest.fixture
def blackboard():

    if crypto.USE_HARDWARE_CRYPTO:
        pytest.skip("Hardware crypto not supported")
        return

    from server.app.blackboard import BlackBoard
    from server.crypto.crypto_state import CryptoState
    crypto_state = CryptoState()
    return BlackBoard(crypto_state)

@patch('server.devices.inverters.modbus_device_scanner.NetworkUtils.get_hosts')
def test_scan_no_hosts_found(mock_get_hosts):
    """Test scanning when no hosts are found"""
    mock_get_hosts.return_value = []
    devices = scan_for_modbus_devices(ports=[502], timeout=NetworkUtils.DEFAULT_TIMEOUT, open_devices=[])
    assert len(devices) == 0

@patch('server.devices.inverters.modbus_device_scanner.ModbusTCP')
@patch('server.devices.inverters.modbus_device_scanner.get_profile_by_manufacturer')
@patch('server.devices.inverters.modbus_device_scanner.NetworkUtils.get_hosts')
def test_scan_finds_single_device(mock_get_hosts, mock_get_profile, mock_modbus_class, 
                                mock_modbus_device, mock_huawei_profile, blackboard):
    """Test scanning finds a single device successfully and saves it to state"""


    
    
    # Setup host info
    host_info = MagicMock(spec=HostInfo)
    host_info.ip = mock_modbus_device.ip
    host_info.port = mock_modbus_device.port
    host_info.mac = mock_modbus_device.mac
    mock_get_hosts.return_value = [host_info]
    
    # Setup profile lookup
    mock_get_profile.return_value = [mock_huawei_profile]
    
    # Use the mock_modbus_device fixture
    mock_modbus_device.device_type = mock_huawei_profile.name
    mock_modbus_device.slave_id = 1
    mock_modbus_class.return_value = mock_modbus_device
    
    # Run test
    devices = scan_for_modbus_devices(ports=[502], timeout=NetworkUtils.DEFAULT_TIMEOUT, open_devices=[])

    # Assertions
    assert len(devices) == 1
    assert devices[0].ip == host_info.ip
    assert devices[0].port == host_info.port
    assert devices[0].mac == host_info.mac
    assert devices[0].device_type == mock_huawei_profile.name
    
    # Verify device was saved to state
    blackboard.set_available_devices(devices=devices)
    saved_devices = blackboard.get_available_devices()
    assert len(saved_devices) == 1
    assert saved_devices[0].ip == host_info.ip
    assert saved_devices[0].port == host_info.port
    assert saved_devices[0].device_type == mock_huawei_profile.name
    assert saved_devices[0].slave_id == 1

def test_filter_out_open_devices():
    """Test filtering out open devices"""
    
    # Create test hosts
    host_1 = HostInfo(
        ip="192.168.1.100",
        port=502,
        mac="00:11:22:33:44:55"
    )
    
    host_2 = HostInfo(
        ip="192.168.1.101",
        port=502,
        mac="00:11:22:33:44:56"
    )
    
    host_3 = HostInfo(
        ip="192.168.1.102",
        port=502,
        mac="00:11:22:33:44:57"
    )
    
    hosts = [host_1, host_2, host_3]
    
    # Create open devices that match some of the hosts
    open_device_1 = MagicMock(spec=ModbusTCP)
    open_device_1.ip = host_1.ip
    open_device_1.port = host_1.port
    open_device_1.mac = host_1.mac
    
    open_device_2 = MagicMock(spec=ModbusTCP)
    open_device_2.ip = host_2.ip
    open_device_2.port = host_2.port
    open_device_2.mac = host_2.mac
    
    open_devices = [open_device_1, open_device_2]
    
    # Test filtering
    from server.devices.inverters.modbus_device_scanner import filter_open_devices
    filtered_hosts = filter_open_devices(hosts, open_devices)
    
    # Verify results
    assert len(filtered_hosts) == 1  # Only host_3 should remain
    assert filtered_hosts[0].ip == host_3.ip
    assert filtered_hosts[0].port == host_3.port
    assert filtered_hosts[0].mac == host_3.mac
    
    # Verify that filtered hosts don't include the open devices
    for host in filtered_hosts:
        for open_device in open_devices:
            assert not (host.ip == open_device.ip and 
                       host.port == open_device.port and 
                       host.mac == open_device.mac)
            
            
def test_get_profile_by_manufacturer():
    """Test getting profiles by manufacturer"""
    
    #  
    
    all_profiles: List[ModbusProfile] = ModbusDeviceProfiles().get_supported_devices()
    
    manufacturer = "HUAWEI TECHNOLOGIES CO.,LTD"
    
    profiles = get_profile_by_manufacturer(manufacturer=manufacturer, profiles=all_profiles)
    
    assert profiles[0].name == "huawei"
    
    assert "huawei" in profiles[0].keywords
