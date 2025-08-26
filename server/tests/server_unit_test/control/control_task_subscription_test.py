from server.control.control_task_subscription import ControlSubscription
from server.control.control_messages.control_message import ControlMessage
from server.app.blackboard import BlackBoard
from unittest.mock import Mock
import pytest
from server.control.control_messages.types import PayloadType, ControlMessageType
from server.devices.profile_keys import RegistersKey, DataTypeKey, EndiannessKey


@pytest.fixture
def control_message():
    obj = {
        PayloadType.TYPE: ControlMessageType.EMS_CONTROL_SCHEDULE,
        PayloadType.PAYLOAD: {
            PayloadType.ID: "8484",
            PayloadType.SN: "f42ea576ac87184445",
            PayloadType.EXECUTE_AT: "2025-02-21T18:53:48.3529926Z",
            PayloadType.PROTOCOL: "modbus",
            PayloadType.COMMANDS: [
                {
                    RegistersKey.START_REGISTER: 1,
                    RegistersKey.NAME: "Fiddle stuff",
                    RegistersKey.DESCRIPTION: "Fiddle stuff",
                    RegistersKey.VALUE: 1337
                }
            ],
            PayloadType.SERIAL_NUMBER: "Sourceful-EMS",
            PayloadType.SIGNATURE: "657909c419915146dc2736ffe406184ccce02bd1f70f933b80ce8d4bcb4ffd0409b4c4f929a4434b0f1a9bc95953e36ce979df9b306eed9c4e4e9c238403c802",
            PayloadType.CREATED_AT: "2025-02-21T18:53:48.352992"
        }
    }
    return ControlMessage(obj)


@pytest.fixture
def read_message():
    obj = {
        PayloadType.TYPE: ControlMessageType.EMS_DATA_REQUEST,
        PayloadType.PAYLOAD: {
            PayloadType.ID: 4188,
            PayloadType.SN: "2311286262",
            PayloadType.COMMANDS: [
                {
                    RegistersKey.START_REGISTER: 587,
                    RegistersKey.NAME: "Voltage",
                    RegistersKey.DESCRIPTION: "The current voltage of the battery",
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.SCALE_FACTOR: 0.1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                    RegistersKey.FUNCTION_CODE: 3
                }
            ],
            PayloadType.SERIAL_NUMBER: "Sourceful-EMS",
            PayloadType.SIGNATURE: "1efcdf2e3936cfac43ca7d62d8ce342d8ea7780c2aa4426b55c1c47886b1214efdf40331f831f1c9d0d21dfc27632736dbf5617a0c0142413b9f94a6b524bf8d",
            PayloadType.CREATED_AT: "2025-04-02T11:43:31.299377"
        }
    }
    return obj


def test_validate_message_signature(control_message):
    control_subscription_obj = ControlSubscription(Mock(spec=BlackBoard))
    assert control_subscription_obj._verify_message_signature(control_message)


def test_handle_device_data_request(read_message):
    control_subscription_obj = ControlSubscription(Mock(spec=BlackBoard))
    control_subscription_obj.handle_ems_data_request(read_message)
