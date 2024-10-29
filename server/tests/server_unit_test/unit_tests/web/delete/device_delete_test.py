import pytest
from unittest.mock import MagicMock
from server.blackboard import BlackBoard
from server.web.handler.delete.device import Handler
from server.web.handler.requestData import RequestData
import server.tests.config_defaults as cfg


@pytest.fixture
def handler():
    return Handler()

@pytest.fixture
def blackboard():
    return BlackBoard()

@pytest.fixture
def mock_device():
    device = MagicMock()
    device.get_config.return_value = cfg.TCP_CONFIG
    device.get_SN.return_value = cfg.TCP_CONFIG['sn']
    return device

def test_delete_existing_device(handler, blackboard, mock_device):
    # Add a device to the blackboard
    blackboard.devices.add(mock_device)
    
    # Create request data with the device's serial number
    post_params = {'id': mock_device.get_config()['sn']}
    request = RequestData(blackboard, post_params, {}, {})
    
    # Execute delete
    status_code, response = handler.do_delete(request)
    
    # Verify response
    assert status_code == 200
    assert len(blackboard.devices.lst) == 0

def test_delete_nonexistent_device(handler, blackboard):
    # Create request data with a non-existent serial number
    post_params = {'id': 'nonexistent_sn'}
    request = RequestData(blackboard, post_params, {}, {})
    
    # Execute delete
    status_code, response = handler.do_delete(request)
    
    # Verify response
    assert status_code == 404

def test_delete_without_serial_number(handler, blackboard):
    # Create request data without a serial number
    request = RequestData(blackboard, {}, {}, {})
    
    # Execute delete
    status_code, response = handler.do_delete(request)
    
    # Verify response
    assert status_code == 400

def test_delete_multiple_devices(handler, blackboard):
    # Add multiple devices to the blackboard
    devices = [MagicMock() for _ in range(3)]
    for i, device in enumerate(devices):
        device.get_config.return_value = {**cfg.TCP_CONFIG, 'sn': f'device_{i}'}
        device.get_SN.return_value = f'device_{i}'
        blackboard.devices.add(device)
    
    # Delete middle device
    post_params = {'id': 'device_1'}
    request = RequestData(blackboard, post_params, {}, {})
    
    # Execute delete
    status_code, response = handler.do_delete(request)
    
    # Verify response
    assert status_code == 200
    assert len(blackboard.devices.lst) == 2
    remaining_sns = [d.get_config()['sn'] for d in blackboard.devices.lst]
    assert 'device_1' not in remaining_sns