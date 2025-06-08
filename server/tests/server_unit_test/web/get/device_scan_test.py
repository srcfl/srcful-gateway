import pytest
from unittest.mock import MagicMock, patch
from server.web.handler.get.device_scan import DeviceScanHandler
from server.web.handler.requestData import RequestData
from server.tests import config_defaults as cfg
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.devices.inverters.ModbusTCP import ModbusTCP
from server.devices.inverters.enphase import Enphase


@pytest.fixture
def setup_handler():
    handler = DeviceScanHandler()
    mock_bb = BlackBoard(MagicMock(spec=CryptoState))
    request_data = RequestData(bb=mock_bb, query_params={}, post_params={}, data={})
    return handler, mock_bb, request_data


@patch('server.tasks.discover_mdns_devices_task.DiscoverMdnsDevicesTask.discover_mdns_devices')
@patch('server.tasks.discoverModbusDevicesTask.DiscoverModbusDevicesTask.discover_modbus_devices')
@patch('server.tasks.discoverDevicesTask.scan_for_p1_devices')
def test_do_get_saves_devices_to_state(mock_scan_p1, mock_scan_modbus, mock_scan_mdns, setup_handler):
    # Arrange
    handler, mock_bb, request_data = setup_handler

    mock_mdns_devices = [
        Enphase(ip=cfg.ENPHASE_CONFIG["ip"])
    ]
    mock_scan_mdns.return_value = mock_mdns_devices

    mock_modbus_devices = [
        ModbusTCP(ip=cfg.TCP_CONFIG["ip"], port=cfg.TCP_CONFIG["port"], mac=cfg.TCP_CONFIG["mac"], device_type=cfg.TCP_CONFIG["device_type"]),
        ModbusTCP(ip=cfg.SOLARMAN_CONFIG["ip"], port=cfg.SOLARMAN_CONFIG["port"], mac=cfg.SOLARMAN_CONFIG["mac"], device_type=cfg.SOLARMAN_CONFIG["device_type"])
    ]

    mock_scan_modbus.return_value = mock_modbus_devices
    mock_scan_p1.return_value = []  # No P1 devices for this test

    status_code, response = handler.do_get(request_data)

    assert mock_scan_modbus.call_count == 1
    assert status_code == 200

    available_devices = mock_bb.get_available_devices()

    assert len(available_devices) == 3
    assert available_devices[0].ip == cfg.TCP_CONFIG["ip"]
    assert available_devices[1].ip == cfg.SOLARMAN_CONFIG["ip"]
