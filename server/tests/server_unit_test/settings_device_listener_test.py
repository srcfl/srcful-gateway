from server.app.settings_device_listener import SettingsDeviceListener
from server.tasks.harvestFactory import HarvestFactory
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.app.settings import ChangeSource
from server.network.network_utils import NetworkUtils
from server.devices.ICom import ICom
import pytest
from unittest.mock import MagicMock, patch
from server.crypto.crypto_state import CryptoState
from server.app.blackboard import BlackBoard
from unittest.mock import Mock


@pytest.fixture
def settings_device_listener(blackboard) -> SettingsDeviceListener:
    ret = SettingsDeviceListener(blackboard)
    blackboard.settings.devices.add_listener(ret._perform_action)   # we hack this to call _perform action directly and avoid the debounce thread
    return ret


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


def test_add_duplicate_connections(settings_device_listener):
    assert_initial_state(settings_device_listener)

    connections = [
        {
            "host": "192.168.0.240",
            "port": 5002,
            "type": "sma",
            "address": 1,
            "connection": "TCP",
            "sn": "duplicate_device"
        },
        {
            "host": "192.168.0.240",
            "port": 5002,
            "type": "sma",
            "address": 2,
            "connection": "TCP",
            "sn": "duplicate_device"
        }
    ]

    # Add to both settings and storage to match current hybrid approach
    settings_device_listener.blackboard.settings.devices._connections = connections
    for connection in connections:
        # Create a mock ICom object for the storage
        mock_device = MagicMock(spec=ICom)
        mock_device.get_config.return_value = connection
        mock_device.get_SN.return_value = connection["sn"]
        settings_device_listener.blackboard.device_storage.add_connection(mock_device)

    settings_device_listener._perform_action(ChangeSource.BACKEND)

    tasks = settings_device_listener.blackboard._tasks

    for task in tasks:
        if isinstance(task, DevicePerpetualTask):
            mock_device_methods(task)
            task.execute(0)

    assert len(settings_device_listener.blackboard.devices.lst) == 1


def test_fetch_device_settings_in_old_format(settings_device_listener: SettingsDeviceListener):
    HarvestFactory(settings_device_listener.blackboard)
    connection = {
        "host": "192.168.0.240",
        "port": 5002,
        "type": "sma",
        "mac": NetworkUtils.INVALID_MAC,
        "slave_id": 1,
        "connection": "TCP",
        "sn": "test_device"
    }

    # Add to both settings and storage to match current hybrid approach
    settings_device_listener.blackboard.settings.devices._connections = [connection]

    # Create a mock ICom object for the storage
    mock_device = MagicMock(spec=ICom)
    mock_device.get_config.return_value = connection
    mock_device.get_SN.return_value = connection["sn"]
    settings_device_listener.blackboard.device_storage.add_connection(mock_device)

    settings_device_listener._perform_action(ChangeSource.BACKEND)  # _connection gets updated at this point to conform to the new format

    task = settings_device_listener.blackboard.purge_tasks()[0]

    assert isinstance(task, DevicePerpetualTask)

    mock_device_methods(task)

    def mock_connect():
        task.device.mac = "00:00:00:00:00:02"  # Set "real" MAC
        return True

    task.device.connect = mock_connect

    task = task.execute(0)

    assert task is None  # Device is opened (mocked above in mock_device_methods), so this should return None

    assert len(settings_device_listener.blackboard.devices.lst) == 1

    assert len(settings_device_listener.blackboard.settings.devices._connections) == 1

    new_config = settings_device_listener.blackboard.settings.devices._connections[0]

    # Assert that the device is updated in settings
    assert new_config == settings_device_listener.blackboard.devices.lst[0].get_config()  # this should break, the MAC is not updated in the settings


def test_remove_faulty_connection(settings_device_listener: SettingsDeviceListener):
    with patch('server.devices.IComFactory.IComFactory.create_com') as mock_create_com:
        mock_create_com.side_effect = ValueError("Test error")

        settings_device_listener.blackboard.settings.devices._connections = [
            {"connection": "TCP", "host": "192.168.1.1", "port": 502, "address": 1, "type": "solaredge", "sn": NetworkUtils.INVALID_MAC}
        ]

        settings_device_listener._perform_action(ChangeSource.BACKEND)

        assert len(settings_device_listener.blackboard.settings.devices._connections) == 0
