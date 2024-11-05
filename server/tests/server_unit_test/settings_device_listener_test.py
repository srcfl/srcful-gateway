from server.settings_device_listener import SettingsDeviceListener
from server.tasks.harvestFactory import HarvestFactory
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.blackboard import BlackBoard
from server.settings import ChangeSource
from server.network.network_utils import NetworkUtils
import pytest 
from unittest.mock import MagicMock
from server.tasks.saveStateTask import SaveStateTask


@pytest.fixture
def blackboard():
    return BlackBoard()

@pytest.fixture
def settings_device_listener(blackboard):
    return SettingsDeviceListener(blackboard)

# @pytest.fixture
def assert_initial_state(settings_device_listener):
    """Helper function to assert the initial state of connections."""
    assert settings_device_listener.blackboard.settings.devices._connections == []

def mock_device_methods(task):
    """Helper function to mock device methods."""
    task.device.connect = MagicMock(return_value=True)
    task.device.is_valid = MagicMock(return_value=True)
    task.device.is_open = MagicMock(return_value=True)

def assert_tasks_are_device_perpetual(tasks):
    """Helper function to assert that tasks are of type DevicePerpetualTask."""
    for task in tasks:
        assert isinstance(task, DevicePerpetualTask)

def test_add_connection_in_old_format(settings_device_listener):
    assert_initial_state(settings_device_listener)
    
    old_config = {
        "connection": "TCP",
        "host": "192.168.1.1",
        "mac": NetworkUtils.INVALID_MAC,
        "port": 502,
        "address": 1,
        "type": "solaredge",
        "sn": NetworkUtils.INVALID_MAC}
    
    settings_device_listener.blackboard.settings.devices._connections = [old_config]
    
    settings_device_listener._perform_action(ChangeSource.LOCAL)
    
    new_config = settings_device_listener.blackboard._tasks[0].device.get_config()
    assert new_config == old_config
    
    assert len(settings_device_listener.blackboard._tasks) == 1
    
    assert_tasks_are_device_perpetual(settings_device_listener.blackboard._tasks)
    
    assert settings_device_listener.blackboard.settings.devices._connections[0] == new_config

def test_add_multiple_connections_in_old_format(settings_device_listener):
    assert_initial_state(settings_device_listener)
    
    settings_device_listener.blackboard.settings.devices._connections = [
        {
          "host": "192.168.0.240",
          "port": 5002,
          "address": 126,
          "connection": "SUNSPEC"
        },
        {
          "host": "192.168.0.240",
          "port": 5002,
          "type": "SMA",
          "address": 1,
          "connection": "TCP"
        }
    ]
    
    settings_device_listener._perform_action(ChangeSource.LOCAL)
    
    assert len(settings_device_listener.blackboard._tasks) == 2
    
    assert_tasks_are_device_perpetual(settings_device_listener.blackboard._tasks)
    
    assert len(settings_device_listener.blackboard.settings.devices._connections) == 2
    
    for task in settings_device_listener.blackboard._tasks:
        assert task.device.get_config() in settings_device_listener.blackboard.settings.devices._connections

def test_add_duplicate_connections(settings_device_listener):
    assert_initial_state(settings_device_listener)
    
    settings_device_listener.blackboard.settings.devices._connections = [
        {
            "host": "192.168.0.240",
            "port": 5002,
            "type": "sma",
            "address": 1,
            "connection": "TCP"
        },
        {
            "host": "192.168.0.240",
            "port": 5002,
            "type": "sma",
            "address": 2,
            "connection": "TCP"
        }
    ]
    
    settings_device_listener._perform_action(ChangeSource.LOCAL)
    
    tasks = settings_device_listener.blackboard._tasks
    
    for task in tasks:
        if isinstance(task, DevicePerpetualTask):
            mock_device_methods(task)
            task.execute(0)
    
    assert len(settings_device_listener.blackboard.devices.lst) == 1

def test_settings_updated_after_device_opened_with_old_format(settings_device_listener):
    settings_device_listener.blackboard.settings.devices._connections = [
        {
            "host": "192.168.0.240",
            "port": 5002,
            "type": "sma",
            "address": 1,
            "connection": "TCP"
        }
    ]
    
    settings_device_listener._perform_action(ChangeSource.LOCAL)
    
    task = settings_device_listener.blackboard._tasks[0]
    
    assert isinstance(task, DevicePerpetualTask)
    
    mock_device_methods(task)
    
    task.execute(0)
    
    assert len(settings_device_listener.blackboard.devices.lst) == 1
    
    conf = settings_device_listener.blackboard.settings.devices._connections[0]
    
    assert settings_device_listener.blackboard.devices.contains(task.device)
    
    assert conf == settings_device_listener.blackboard.devices.lst[0].get_config()
    

def test_fetch_device_settings_in_old_format(settings_device_listener):
    # HarvestFactory(settings_device_listener.blackboard)
    settings_device_listener.blackboard.settings.devices._connections = [
        {
            "host": "192.168.0.240",
            "port": 5002,
            "type": "sma",
            "mac": NetworkUtils.INVALID_MAC,
            "slave_id": 1,
            "connection": "TCP"
        }
    ]
    settings_device_listener._perform_action(ChangeSource.BACKEND) # _connection gets updated at this point to conform to the new format
    
    task = settings_device_listener.blackboard._tasks[0]
    
    assert isinstance(task, DevicePerpetualTask)
    
    mock_device_methods(task)
    
    task = settings_device_listener.blackboard.purge_tasks()
    
    task = task[0]
    
    def mock_connect():
        task.device.mac = "00:00:00:00:00:02"  # Set "real" MAC
        return True
    
    task.device.connect = mock_connect
    
    task = task.execute(0)
    
    assert task is None # Device is opened (mocked above in mock_device_methods), so this should return None
    
    assert len(settings_device_listener.blackboard.devices.lst) == 1
    
    assert len(settings_device_listener.blackboard.settings.devices._connections) == 1
    
    new_config = settings_device_listener.blackboard.settings.devices._connections[0]
    
    # Assert that the device is updated in settings
    assert new_config == settings_device_listener.blackboard.devices.lst[0].get_config() # this should break, the MAC is not updated in the settings