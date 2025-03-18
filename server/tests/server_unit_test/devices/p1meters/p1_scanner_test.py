import pytest
from unittest.mock import patch, Mock
from server.devices.p1meters.p1_scanner import (
    scan_for_p1_device,
    scan_for_p1_devices,
    _ScanInfo,
    _mdns_scan_for_devices,
    _get_scan_info
)
from server.network.network_utils import HostInfo, NetworkUtils
from server.network.mdns.mdns import ServiceResult
from server.devices.ICom import ICom


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
def mock_device():
    device = Mock(spec=ICom)
    device.connect.return_value = True
    return device


@pytest.fixture
def mock_scan_info(mock_device):
    factory = Mock(return_value=mock_device)
    return _ScanInfo(
        domain_names={"_test._tcp.local.": {"name": "test"}},
        ports=[80],
        factory_method_msn=factory
    )


def test_scan_info_scan_for_device(mock_scan_info, mock_host):
    # Setup
    with patch('server.devices.p1meters.p1_scanner._mdns_scan_for_devices', return_value=[mock_host]), \
            patch('server.devices.p1meters.p1_scanner.NetworkUtils.get_hosts', return_value=[]):

        # Test
        device = mock_scan_info.scan_for_device("TEST123")

        # Verify
        assert device is not None
        mock_scan_info.factory_method_msn.assert_called_once_with("TEST123", mock_host)


def test_scan_info_scan_for_devices(mock_scan_info, mock_host):
    # Setup
    with patch('server.devices.p1meters.p1_scanner._mdns_scan_for_devices', return_value=[mock_host]), \
            patch('server.devices.p1meters.p1_scanner.NetworkUtils.get_hosts', return_value=[]):

        # Test
        devices = mock_scan_info.scan_for_devices()

        # Verify
        assert len(devices) == 1
        mock_scan_info.factory_method_msn.assert_called_once_with(None, mock_host)


@patch('server.devices.p1meters.p1_scanner._get_scan_info')
def test_scan_for_p1_device_found(mock_get_scan_info, mock_scan_info, mock_device):
    # Setup
    mock_get_scan_info.return_value = [mock_scan_info]
    mock_mdns_service = Mock(spec=ServiceResult)
    mock_mdns_service.address = "192.168.1.100"
    mock_mdns_service.port = 80
    with patch('server.network.mdns.mdns.scan', return_value=[mock_mdns_service]):

        # Test
        result = scan_for_p1_device("TEST123")

    # Verify
    assert result == mock_device
    mock_get_scan_info.assert_called_once()


@patch('server.devices.p1meters.p1_scanner._get_scan_info')
def test_scan_for_p1_device_not_found(mock_get_scan_info, mock_scan_info):
    # Setup
    mock_scan_info.factory_method_msn.return_value = None
    mock_get_scan_info.return_value = [mock_scan_info]

    # neither mdns nor network scan found any devices
    with patch('server.network.mdns.mdns.scan', return_value=[]), \
            patch('server.devices.p1meters.p1_scanner.NetworkUtils.get_hosts', return_value=[]):

        # Test
        result = scan_for_p1_device("TEST123")

    # Verify
    assert result is None
    mock_get_scan_info.assert_called_once()


@patch('server.devices.p1meters.p1_scanner._get_scan_info')
def test_scan_for_p1_devices(mock_get_scan_info, mock_scan_info, mock_device):
    # Setup
    mock_get_scan_info.return_value = [mock_scan_info]

    # mdns did not find any devices but network scan did
    with patch('server.network.mdns.mdns.scan', return_value=[]), \
            patch('server.devices.p1meters.p1_scanner.NetworkUtils.get_hosts', return_value=[HostInfo("192.168.1.100", 80, NetworkUtils.INVALID_MAC)]):

        # Test
        results = scan_for_p1_devices()

    # Verify
    assert len(results) == 1
    assert results[0] == mock_device
    mock_get_scan_info.assert_called_once()


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
    mock_mdns_scan.assert_called_once_with(5, "_test._tcp.local.")


def test_get_scan_info():
    # Test
    scan_infos = _get_scan_info()

    # Verify
    assert len(scan_infos) == 2

    # Verify Telnet config
    telnet_info = scan_infos[0]
    assert telnet_info.ports == [23]
    assert "_currently._tcp.local." in telnet_info.domain_names
