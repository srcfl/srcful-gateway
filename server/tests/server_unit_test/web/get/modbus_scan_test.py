import pytest
from unittest.mock import MagicMock, patch
from server.web.handler.get.modbus_scan import ModbusScanHandler
from server.web.handler.requestData import RequestData
from server.network.network_utils import HostInfo
from server.tests import config_defaults as cfg
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState

@pytest.fixture
def setup_handler():
    handler = ModbusScanHandler()
    mock_bb = BlackBoard(MagicMock(spec=CryptoState))
    # mock_bb.set_available_devices = MagicMock()
    request_data = RequestData(bb=mock_bb, query_params={}, post_params={}, data={})
    return handler, mock_bb, request_data

@patch('server.network.network_utils.NetworkUtils.get_hosts')
def test_do_get_saves_devices_to_state(mock_get_hosts, setup_handler):
    # Arrange
    handler, mock_bb, request_data = setup_handler
    
    # Create HostInfo objects that NetworkUtils.get_hosts would return
    mock_hosts = [
        HostInfo(ip=cfg.TCP_CONFIG["ip"], 
                port=cfg.TCP_CONFIG["port"],
                mac=cfg.TCP_CONFIG.get("mac", "00:00:00:00:00:00")),
        HostInfo(ip=cfg.SOLARMAN_CONFIG["ip"],
                port=cfg.SOLARMAN_CONFIG["port"],
                mac=cfg.SOLARMAN_CONFIG.get("mac", "00:00:00:00:00:00"))
    ]
    
    mock_get_hosts.return_value = mock_hosts


    status_code, response = handler.do_get(request_data)

    assert status_code == 200
    
    available_devices = mock_bb.get_available_devices()
    
    assert len(available_devices) == 2
    assert available_devices[0].ip == cfg.TCP_CONFIG["ip"]
    assert available_devices[1].ip == cfg.SOLARMAN_CONFIG["ip"]
