from server.web.socket.control.control_task_registry import TaskExecutionRegistry
from server.web.socket.control.control_messages.base_message import BaseMessage
from server.web.socket.control.control_messages.control_message import ControlMessage
from server.tasks.control_device_task import ControlDeviceTask
from server.tests.server_unit_test.web.socket.control.message_structure_test import ems_control_schedule_message
from server.app.blackboard import BlackBoard
from unittest.mock import Mock
from server.crypto.crypto_state import CryptoState
import pytest
import server.tests.config_defaults as cfg
from server.devices.ICom import ICom
from server.web.socket.control.control_messages.types import PayloadType, ControlMessageType


message_id = 563


@pytest.fixture
def control_message():
    control_message = ControlMessage(ems_control_schedule_message)
    control_message.id = message_id
    return control_message


@pytest.fixture
def blackboard():
    return BlackBoard(Mock(spec=CryptoState))


@pytest.fixture
def cancel_message():
    return BaseMessage(
        {
            PayloadType.TYPE: ControlMessageType.EMS_CONTROL_SCHEDULE_CANCEL,
            PayloadType.PAYLOAD: {
                PayloadType.ID: message_id,
                PayloadType.SN: "2311286262",
                PayloadType.SERIAL_NUMBER: "Sourceful-EMS",
                PayloadType.SIGNATURE: "88c0efa7577919952746bf38366f250bb9b336cf9e2961a5e21b60bd44267282976009a6b3400ed9825a725a090021a725866fc979aa935adde280b66e79be71",
                PayloadType.CREATED_AT: "2025-03-11T13:58:00.434799"
            }
        }
    )


@pytest.fixture
def open_device():
    device = Mock(spec=ICom)
    device.is_open.return_value = True
    device.get_config.return_value = cfg.TCP_ARGS
    device.get_SN.return_value = "2311286262"
    return device


def test_add_task(control_message, blackboard):
    registry = TaskExecutionRegistry()
    task = ControlDeviceTask(blackboard.time_ms(), blackboard, control_message)
    registry.add_task(task)

    assert registry.size == 1

    assert registry.get_task(control_message.id) == task


def test_task_cacelled_from_registry(control_message, blackboard, cancel_message):
    registry = TaskExecutionRegistry()
    task = ControlDeviceTask(blackboard.time_ms(), blackboard, control_message)
    registry.add_task(task)

    registry.get_task(cancel_message.id).cancel()

    assert registry.get_task(cancel_message.id).is_cancelled
