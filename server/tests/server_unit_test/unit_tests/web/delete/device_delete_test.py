import pytest
from unittest.mock import MagicMock
from server.blackboard import BlackBoard
from server.settings_device_listener import SettingsDeviceListener
from server.tasks.harvestFactory import HarvestFactory
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
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
    data_params = {'id': mock_device.get_config()['sn']}
    request = RequestData(blackboard, {}, {}, data_params)
    
    # Execute delete
    status_code, response = handler.do_delete(request)
    
    # Verify response
    assert status_code == 200
    assert len(blackboard.devices.lst) == 0

def test_delete_nonexistent_device(handler, blackboard):
    # Create request data with a non-existent serial number
    data_params = {'id': 'nonexistent_sn'}
    request = RequestData(blackboard, {}, {}, data_params)
    
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
    data_params = {'id': 'device_1'}
    request = RequestData(blackboard, {}, {}, data_params)
    
    # Execute delete
    status_code, response = handler.do_delete(request)
    
    # Verify response
    assert status_code == 200
    assert len(blackboard.devices.lst) == 2
    remaining_sns = [d.get_config()['sn'] for d in blackboard.devices.lst]
    assert 'device_1' not in remaining_sns

def test_delete_device_with_perpetual_task(handler, blackboard, mock_device):


    # set up the listeners
    settings_device_listener = SettingsDeviceListener(blackboard)
    harvest_factory = HarvestFactory(blackboard)

    blackboard.devices.add_listener(harvest_factory)
    blackboard.settings.devices.add_listener(settings_device_listener.on_change)


    # Add a device to the blackboard
    blackboard.devices.add(mock_device)

    # make sure the device is closed
    mock_device.is_open.return_value = False

    # create a perpetual task
    cloned_device = mock_device.clone()
    cloned_device.is_open.return_value = False

    task = DevicePerpetualTask(0, blackboard, cloned_device)

    # delete the device
    data_params = {'id': mock_device.get_config()['sn']}
    request = RequestData(blackboard, {}, {}, data_params)

    # execute delete
    status_code, response = handler.do_delete(request)

    # verify response
    assert status_code == 200
    assert len(blackboard.devices.lst) == 0
    
    # check that the perpetual task does not execute and returns None
    assert task.execute(0) == None

    assert cloned_device.connect.call_count == 0
    assert len(blackboard.devices.lst) == 0
