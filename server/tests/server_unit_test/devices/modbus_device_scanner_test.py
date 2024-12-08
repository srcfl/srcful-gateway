# from unittest.mock import patch
# import pytest
# from server.devices.inverters.modbus_device_scanner import scan_for_modbus_devices, try_profile
# from server.network.network_utils import HostInfo
# from server.devices.supported_devices.profiles import ModbusDeviceProfiles

# @pytest.fixture
# def test_host():
#     return HostInfo(ip="192.168.1.100", port=502, mac="00:11:22:33:44:55")

# @pytest.fixture
# def device_profiles():
#     profiles = ModbusDeviceProfiles().get_supported_devices()
#     return {
#         'huawei': next(p for p in profiles if p.name == "huawei"),
#         'sungrow': next(p for p in profiles if p.name == "sungrow")
#     }

# @patch('server.network.network_utils.NetworkUtils.get_hosts')
# def test_scan_no_hosts_found(mock_get_hosts):
#     """Test scanning when no hosts are found"""
#     mock_get_hosts.return_value = []
#     devices = scan_for_modbus_devices()
#     assert len(devices) == 0

# @patch('server.network.network_utils.NetworkUtils.get_hosts')
# @patch('server.devices.inverters.ModbusTCP.ModbusTCP.connect')
# @patch('server.devices.inverters.ModbusTCP.ModbusTCP.read_registers')
# def test_full_scan_with_multiple_devices(mock_read_registers, mock_connect, mock_get_hosts):
#     """Test full scan with multiple devices found"""
#     # Setup mocks
#     mock_get_hosts.return_value = [
#         HostInfo(ip="192.168.1.100", port=502, mac="00:11:22:33:44:55"),
#         HostInfo(ip="192.168.1.101", port=502, mac="00:11:22:33:44:66")
#     ]
    
#     mock_connect.return_value = True
#     mock_read_registers.side_effect = [
#         [5000],  # First device - 50Hz
#         [5100]   # Second device - 51Hz
#     ]
    
#     # Test full scan
#     devices = scan_for_modbus_devices()
#     assert len(devices) == 2

