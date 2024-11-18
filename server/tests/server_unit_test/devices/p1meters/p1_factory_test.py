import pytest
from unittest.mock import patch, Mock
from server.devices.p1meters.p1_factory import create_rest_device_msn, create_telnet_device_msn
from server.network.network_utils import HostInfo
from server.devices.ICom import ICom

@pytest.fixture
def host_info():
    return HostInfo(ip="192.168.1.100", port=80, mac="00:00:00:00:00:00")

@pytest.fixture
def meter_serial_number():
    return "TEST123"

@patch('server.devices.p1meters.P1Jemac.P1Jemac')  
def test_create_rest_device_success(mock_p1jemac, host_info, meter_serial_number):
    mock_device = Mock(spec=ICom)
    mock_device.connect.return_value = True
    mock_p1jemac.return_value = mock_device

    device = create_rest_device_msn(meter_serial_number, host_info)

    mock_p1jemac.assert_called_once_with(host_info.ip, host_info.port, meter_serial_number)
    mock_device.connect.assert_called_once()
    assert device == mock_device

@patch('server.devices.p1meters.P1Jemac.P1Jemac')  
def test_create_rest_device_failure(mock_p1jemac, host_info, meter_serial_number):
    mock_device = Mock(spec=ICom)
    mock_device.connect.return_value = False
    mock_p1jemac.return_value = mock_device

    device = create_rest_device_msn(meter_serial_number, host_info)

    mock_p1jemac.assert_called_once_with(host_info.ip, host_info.port, meter_serial_number)
    mock_device.connect.assert_called_once()
    assert device is None

@patch('server.devices.p1meters.P1Telnet.P1Telnet')
def test_create_telnet_device_success(mock_p1telnet, host_info, meter_serial_number):
    mock_device = Mock(spec=ICom)
    mock_device.connect.return_value = True
    mock_p1telnet.return_value = mock_device

    device = create_telnet_device_msn(meter_serial_number, host_info)

    mock_p1telnet.assert_called_once_with(host_info.ip, host_info.port, meter_serial_number)
    mock_device.connect.assert_called_once()
    assert device == mock_device

@patch('server.devices.p1meters.P1Telnet.P1Telnet')
def test_create_telnet_device_failure(mock_p1telnet, host_info, meter_serial_number):
    mock_device = Mock(spec=ICom)
    mock_device.connect.return_value = False
    mock_p1telnet.return_value = mock_device

    device = create_telnet_device_msn(meter_serial_number, host_info)

    mock_p1telnet.assert_called_once_with(host_info.ip, host_info.port, meter_serial_number)
    mock_device.connect.assert_called_once()
    assert device is None


@patch('server.devices.p1meters.p1_factory._connect_device')
def test_create_rest_device_constructor(mock_connect, host_info, meter_serial_number):
    # Setup
    mock_device = Mock()
    mock_connect.return_value = mock_device

    # Test
    device = create_rest_device_msn(meter_serial_number, host_info)

    # Verify
    assert device == mock_device
    mock_connect.assert_called_once()
    
    # Get the actual arguments passed to _connect_device
    args = mock_connect.call_args
    device_arg = args[0][0]  # First positional argument (p1 device)
    error_msg = args[0][1]   # Second positional argument (error message)
    
    # Verify the P1Jemac was constructed correctly
    assert device_arg.ip == host_info.ip
    assert device_arg.port == host_info.port
    assert device_arg.meter_serial_number == meter_serial_number

@patch('server.devices.p1meters.p1_factory._connect_device')
def test_create_telnet_device_constructor(mock_connect, host_info, meter_serial_number):
    # Setup
    mock_device = Mock()
    mock_connect.return_value = mock_device

    # Test
    device = create_telnet_device_msn(meter_serial_number, host_info)

    # Verify
    assert device == mock_device
    mock_connect.assert_called_once()
    
    # Get the actual arguments passed to _connect_device
    args = mock_connect.call_args
    device_arg = args[0][0]  # First positional argument (p1 device)
    error_msg = args[0][1]   # Second positional argument (error message)
    
    # Verify the P1Telnet was constructed correctly
    assert device_arg.ip == host_info.ip
    assert device_arg.port == host_info.port
    assert device_arg.meter_serial_number == meter_serial_number