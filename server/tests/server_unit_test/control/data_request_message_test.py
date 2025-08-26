from unittest.mock import Mock
from server.control.control_messages.read_message import ReadMessage
from server.control.control_messages.types import ControlMessageType, PayloadType
from server.devices.profile_keys import RegistersKey, DataTypeKey, EndiannessKey
from server.devices.ICom import ICom
import pytest


@pytest.fixture
def ems_data_request_message():
    return {
        PayloadType.TYPE: ControlMessageType.EMS_DATA_REQUEST,
        PayloadType.PAYLOAD: {
            PayloadType.ID: 1356,
            PayloadType.SN: "2311286262",
            PayloadType.EXECUTE_AT: "2025-03-14T15:00:00.000000",
            PayloadType.PROTOCOL: "modbus",
            PayloadType.COMMANDS: [
                {
                    RegistersKey.START_REGISTER: 587,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.FUNCTION_CODE: 4,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.SCALE_FACTOR: 0.1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG
                }
            ],
            PayloadType.SERIAL_NUMBER: "Sourceful-EMS",
            PayloadType.SIGNATURE: "2a69d5eecf7c1f564e1be1e8b15711b009a66d5b8448e9b32ead40e5e741ec56294034d18212c260a5285beffcc0fef00708807e96cd296b3d0b301ddea1a45c",
            PayloadType.CREATED_AT: "2025-03-14T13:58:00.338870"
        }
    }


def test_process_commands(ems_data_request_message):
    data_request_message: ReadMessage = ReadMessage(ems_data_request_message)

    data_request_message.process_commands(Mock(spec=ICom))

    assert data_request_message.commands[0].register == 587
    assert data_request_message.commands[0].num_of_registers == 1
    assert data_request_message.commands[0].function_code == 4
    assert data_request_message.commands[0].data_type == DataTypeKey.U16
    assert data_request_message.commands[0].scale_factor == 0.1
    assert data_request_message.commands[0].endianness == EndiannessKey.BIG

    assert data_request_message.commands[0].value == 0  # No value was read (default value in RegisterValue class, since device is just mocked)
