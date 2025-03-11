from server.web.socket.control.control_task_registry import TaskExecutionRegistry
from server.web.socket.control.control_messages.control_message import ControlMessage
from server.tasks.control_device_task import ControlDeviceTask
from server.tests.server_unit_test.web.socket.control.message_structure_test import ems_control_schedule_message
from server.app.blackboard import BlackBoard
from unittest.mock import Mock
from server.crypto.crypto_state import CryptoState
import pytest
import server.tests.config_defaults as cfg
from server.devices.ICom import ICom


@pytest.fixture
def control_message():
    return ControlMessage(ems_control_schedule_message)


@pytest.fixture
def blackboard():
    return BlackBoard(Mock(spec=CryptoState))


@pytest.fixture
def open_device():
    device = Mock(spec=ICom)
    device.is_open.return_value = True
    device.get_config.return_value = cfg.TCP_ARGS
    device.get_SN.return_value = "2311286262"
    return device


def test_update_task(control_message, blackboard):
    registry = TaskExecutionRegistry()
    task = ControlDeviceTask(blackboard.time_ms(), blackboard, control_message)
    registry.add_task(task)

    assert len(registry.get_tasks()) == 1
    assert registry.get_task(control_message.id) == task


def test_task_cancelled(control_message, blackboard):
    registry = TaskExecutionRegistry()
    task = ControlDeviceTask(blackboard.time_ms(), blackboard, control_message)
    registry.add_task(task)

    task.cancel()

    assert task.is_cancelled
    assert registry.get_task(control_message.id).is_cancelled
