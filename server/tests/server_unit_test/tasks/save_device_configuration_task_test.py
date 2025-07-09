import pytest
from unittest.mock import Mock
from server.tests.config_defaults import TCP_ARGS, TCP_CONFIG
from server.devices.IComFactory import IComFactory
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.tasks.save_device_configuration_task import SaveDeviceConfigurationTask
from server.app.settings import ChangeSource


@pytest.fixture
def device_one():
    return IComFactory.create_com(TCP_ARGS)


def test_save_device_configurations_task(device_one, blackboard):
    # Mock the get_SN method to return a specific value
    device_one.get_SN = Mock(return_value="1234567890")
    device_one.get_config = Mock(return_value=TCP_CONFIG)

    sn = device_one.get_SN()
    assert sn == "1234567890"

    device_one.is_open = Mock(return_value=True)
    blackboard.settings.devices.add_connection(device_one, ChangeSource.LOCAL)

    task = SaveDeviceConfigurationTask(0, blackboard)
    task.execute(0)
    assert task.reply.status_code == 200
