import pytest
from unittest.mock import MagicMock, patch
from server.web.handler.get.modbus_scan import ModbusScanHandler
from server.web.handler.requestData import RequestData
from server.tests import config_defaults as cfg
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.devices.inverters.ModbusTCP import ModbusTCP


@pytest.fixture
def setup_handler():
    handler = ModbusScanHandler()
    mock_bb = BlackBoard(MagicMock(spec=CryptoState))
    # mock_bb.set_available_devices = MagicMock()
    request_data = RequestData(bb=mock_bb, query_params={}, post_params={}, data={})
    return handler, mock_bb, request_data

@patch('server.web.handler.get.modbus_scan.scan_for_modbus_devices')
def test_do_get_saves_devices_to_state(mock_scan_for_modbus_devices, setup_handler):
    # Arrange
    handler, mock_bb, request_data = setup_handler
    
    
    mock_devices = [
        ModbusTCP(ip=cfg.TCP_CONFIG["ip"], port=cfg.TCP_CONFIG["port"], mac=cfg.TCP_CONFIG["mac"]),
        ModbusTCP(ip=cfg.SOLARMAN_CONFIG["ip"], port=cfg.SOLARMAN_CONFIG["port"], mac=cfg.SOLARMAN_CONFIG["mac"])
    ]
    
    mock_scan_for_modbus_devices.return_value = mock_devices

    status_code, response = handler.do_get(request_data)
    
    assert mock_scan_for_modbus_devices.call_count == 1

    assert status_code == 200
    
    available_devices = mock_bb.get_available_devices()
    
    assert len(available_devices) == 2
    assert available_devices[0].ip == cfg.TCP_CONFIG["ip"]
    assert available_devices[1].ip == cfg.SOLARMAN_CONFIG["ip"]
    


