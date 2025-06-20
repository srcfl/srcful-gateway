import pytest
from unittest.mock import Mock, MagicMock
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.devices.ICom import ICom
from server.tasks.deviceTask import DeviceTask
from server.tasks.harvestFactory import HarvestFactory
from server.tasks.harvest import Harvest
import server.tests.config_defaults as config_defaults


@pytest.fixture
def mock_device():
    device = MagicMock(spec=ICom)
    device.is_open.return_value = True
    device.get_name.return_value = "Test Device"
    device.get_SN.return_value = "123456"
    device.get_config.return_value = config_defaults.P1_JEMAC_ARGS
    return device


def test_create_harvest_factory(blackboard):
    factory = HarvestFactory(blackboard)
    assert factory is not None
    assert factory.bb == blackboard


def test_add_device_creates_device_task(blackboard, mock_device):
    factory = HarvestFactory(blackboard)

    assert len(blackboard.messages) == 0

    factory.add_device(mock_device)

    # Verify harvest task was created and we have added an info message
    tasks = blackboard.purge_tasks()
    assert len(tasks) > 0
    assert isinstance(tasks[0], DeviceTask)
    assert len(blackboard.messages) > 0

    # Verify device was added to settings
    assert mock_device.get_config() in blackboard.settings.devices.connections


def test_add_closed_device_no_harvest_task(blackboard, mock_device):
    mock_device.is_open.return_value = False
    factory = HarvestFactory(blackboard)

    factory.add_device(mock_device)

    # Verify that both the harvest and the save_config tasks were created
    # this is a change so we don't end up with zombie devices
    tasks = blackboard.purge_tasks()
    assert len(tasks) == 2


def test_remove_device(blackboard, mock_device):
    factory = HarvestFactory(blackboard)

    # First add the device
    factory.add_device(mock_device)
    assert mock_device.get_config() in blackboard.settings.devices.connections

    message_count = len(blackboard.messages)

    # Then remove it
    factory.remove_device(mock_device)

    # Verify device was disconnected
    mock_device.disconnect.assert_called_once()

    # Verify device was removed from settings
    assert mock_device.get_config() not in blackboard.settings.devices.connections

    assert len(blackboard.messages) > message_count


def test_remove_device_already_disconnected(blackboard, mock_device):
    factory = HarvestFactory(blackboard)
    mock_device.disconnect.side_effect = ValueError("Already disconnected")

    factory.add_device(mock_device)
    factory.remove_device(mock_device)

    # Should handle the ValueError gracefully
    mock_device.disconnect.assert_called_once()
    assert mock_device.get_config() not in blackboard.settings.devices.connections


def test_factory_listens_to_blackboard_devices(blackboard, mock_device):
    factory = HarvestFactory(blackboard)

    # Verify factory was added as listener
    assert factory in blackboard.devices._observers
