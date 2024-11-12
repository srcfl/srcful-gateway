import pytest
from unittest.mock import patch, Mock
from server.devices.p1meters import p1_factory
from server.devices.p1meters.p1_scanner import (
    scan_for_p1_device,
    _scan_for_device,
    _mdns_scan_for_devices,
    _scan_for_rest_device,
    _scan_for_telnet_device
)
from server.network.network_utils import HostInfo, NetworkUtils
from server.network.mdns import ServiceResult

@pytest.fixture
def mock_host():
    return HostInfo(ip="192.168.1.100", port=80, mac=NetworkUtils.INVALID_MAC)

@pytest.fixture
def mock_mdns_service():
    service = Mock(spec=ServiceResult)
    service.address = "192.168.1.100"
    service.port = 80
    return service

@pytest.fixture
def meter_serial_number():
    return "TEST123"

@patch('server.devices.p1meters.p1_scanner._scan_for_rest_device')
@patch('server.devices.p1meters.p1_scanner._scan_for_telnet_device')
def test_scan_for_p1_device_rest_found(mock_telnet_scan, mock_rest_scan, meter_serial_number):
    # Setup
    mock_device = Mock()
    mock_rest_scan.return_value = mock_device
    mock_telnet_scan.return_value = None

    # Test
    result = scan_for_p1_device(meter_serial_number)

    # Verify
    assert result == mock_device
    mock_rest_scan.assert_called_once_with(meter_serial_number)
    mock_telnet_scan.assert_not_called()

@patch('server.devices.p1meters.p1_scanner._scan_for_rest_device')
@patch('server.devices.p1meters.p1_scanner._scan_for_telnet_device')
def test_scan_for_p1_device_telnet_found(mock_telnet_scan, mock_rest_scan, meter_serial_number):
    # Setup
    mock_device = Mock()
    mock_rest_scan.return_value = None
    mock_telnet_scan.return_value = mock_device

    # Test
    result = scan_for_p1_device(meter_serial_number)

    # Verify
    assert result == mock_device
    mock_rest_scan.assert_called_once_with(meter_serial_number)
    mock_telnet_scan.assert_called_once_with(meter_serial_number)

@patch('server.devices.p1meters.p1_scanner.mdns.scan')
def test_mdns_scan_for_devices(mock_mdns_scan, mock_mdns_service):
    # Setup
    mock_mdns_scan.return_value = [mock_mdns_service]

    # Test
    hosts = _mdns_scan_for_devices("_test._tcp.local.")

    # Verify
    assert len(hosts) == 1
    assert hosts[0].ip == mock_mdns_service.address
    assert hosts[0].port == mock_mdns_service.port
    assert hosts[0].mac == NetworkUtils.INVALID_MAC
    mock_mdns_scan.assert_called_once_with(5, "_test._tcp.local.")

@patch('server.devices.p1meters.p1_scanner._scan_for_device')
def test_scan_for_rest_device(mock_scan_device, meter_serial_number):
    # Setup
    mock_device = Mock()
    mock_scan_device.return_value = mock_device

    # Test
    result = _scan_for_rest_device(meter_serial_number)

    # Verify
    assert result == mock_device
    mock_scan_device.assert_called_once_with(
        meter_serial_number,
        {"_jemacp1._tcp.local.": {"name": "currently_one"}},
        [80],
        p1_factory.create_rest_device
    )

@patch('server.devices.p1meters.p1_scanner._scan_for_device')
def test_scan_for_telnet_device(mock_scan_device, meter_serial_number):
    # Setup
    mock_device = Mock()
    mock_scan_device.return_value = mock_device

    # Test
    result = _scan_for_telnet_device(meter_serial_number)

    # Verify
    assert result == mock_device
    mock_scan_device.assert_called_once_with(
        meter_serial_number,
        {"_currently._tcp.local.": {"name": "currently_one"}},
        [23],
        p1_factory.create_telnet_device
    )

@patch('server.devices.p1meters.p1_scanner._mdns_scan_for_devices')
@patch('server.devices.p1meters.p1_scanner.NetworkUtils.get_hosts')
def test_scan_for_device_mdns_found(mock_get_hosts, mock_mdns_scan, mock_host, meter_serial_number):
    # Setup
    mock_mdns_scan.return_value = [mock_host]
    mock_factory = Mock()
    mock_device = Mock()
    mock_factory.return_value = mock_device

    # Test
    result = _scan_for_device(
        meter_serial_number,
        {"_test._tcp.local.": {"name": "test"}},
        [80],
        mock_factory
    )

    # Verify
    assert result == mock_device
    mock_mdns_scan.assert_called_once()
    mock_get_hosts.assert_not_called()
    mock_factory.assert_called_once_with(meter_serial_number, mock_host)

@patch('server.devices.p1meters.p1_scanner._mdns_scan_for_devices')
@patch('server.devices.p1meters.p1_scanner.NetworkUtils.get_hosts')
def test_scan_for_device_network_scan_found(mock_get_hosts, mock_mdns_scan, mock_host, meter_serial_number):
    # Setup
    mock_mdns_scan.return_value = []
    mock_get_hosts.return_value = [mock_host]
    mock_factory = Mock()
    mock_device = Mock()
    mock_factory.return_value = mock_device

    # Test
    result = _scan_for_device(
        meter_serial_number,
        {"_test._tcp.local.": {"name": "test"}},
        [80],
        mock_factory
    )

    # Verify
    assert result == mock_device
    mock_mdns_scan.assert_called_once()
    mock_get_hosts.assert_called_once_with([80], 5)
    mock_factory.assert_called_once_with(meter_serial_number, mock_host)