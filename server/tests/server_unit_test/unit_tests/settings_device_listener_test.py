from server.settings_device_listener import SettingsDeviceListener
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.blackboard import BlackBoard
from server.settings import ChangeSource
import pytest 


@pytest.fixture
def blackboard():
    return BlackBoard()

@pytest.fixture
def settings_device_listener(blackboard):
    return SettingsDeviceListener(blackboard)

def test_add_connection_in_old_format(settings_device_listener):
    
    assert settings_device_listener.blackboard.settings.devices._connections == []
    
    old_config = {
        "connection": "TCP",
        "host": "192.168.1.1",
        "mac": "00:00:00:00:00:00",
        "port": 502,
        "address": 1,
        "type": "solaredge",
        "sn": "00:00:00:00:00:00"}
    
    settings_device_listener.blackboard.settings.devices._connections = [old_config]
    
    settings_device_listener._perform_action(ChangeSource.LOCAL) # This updates the connection format in the settings
    
    new_config = settings_device_listener.blackboard._tasks[0].device.get_config()
    assert new_config == old_config
    
    assert len(settings_device_listener.blackboard._tasks) == 1
    
    assert isinstance(settings_device_listener.blackboard._tasks[0], DevicePerpetualTask)
    
    # Assert that the connection was removed from the settings since it was in the old format
    # The blackboard will add the config in the new format once we successfully connect to the device
    assert settings_device_listener.blackboard.settings.devices._connections[0] == new_config
    
    
    
