from server.tasks.control_device_task import ControlDeviceTask
from server.devices.ICom import ICom
import server.tests.config_defaults as cfg
from unittest.mock import Mock
import pytest
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.control.control_messages.control_message import ControlMessage
from server.tests.server_unit_test.control.message_structure_test import ems_control_schedule_message


@pytest.fixture
def control_message():
    return ControlMessage(ems_control_schedule_message)


@pytest.fixture
def open_device():
    device = Mock(spec=ICom)
    device.is_open.return_value = True
    device.get_config.return_value = cfg.TCP_ARGS
    device.get_SN.return_value = "2311286262"
    return device


def test_task_executed(control_message, blackboard, open_device):

    task = ControlDeviceTask(blackboard.time_ms(), blackboard, control_message)

    blackboard.devices.add(open_device)

    assert not task.is_executed
    task.execute(blackboard.time_ms())
    assert task.is_executed


def test_task_cancelled(control_message, blackboard):

    task = ControlDeviceTask(blackboard.time_ms(), blackboard, control_message)
    task.cancel()

    assert task.is_cancelled
