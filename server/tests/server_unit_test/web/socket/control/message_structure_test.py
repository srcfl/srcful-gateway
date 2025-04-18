from server.web.socket.control.control_messages.base_message import BaseMessage
from server.web.socket.control.control_messages.auth_challenge_message import AuthChallengeMessage
from server.web.socket.control.control_messages.control_message import ControlMessage
from server.web.socket.control.control_messages.read_message import ReadMessage
from server.web.socket.control.control_messages.types import PayloadType, ControlMessageType
from server.devices.profile_keys import RegistersKey, DataTypeKey, EndiannessKey

ems_authentication_challenge_message = {
    PayloadType.TYPE: ControlMessageType.EMS_AUTHENTICATION_CHALLENGE,
    PayloadType.PAYLOAD: {
        PayloadType.MESSAGE: "Please send authentication message",
        PayloadType.SERIAL_NUMBER: "Sourceful-EMS",
        PayloadType.SIGNATURE: "56f95bf2c6a0dba9de677b8328ab9fea7bda3312cf9f1fac8a6f2cbe439ddfc16f185c1e00f0cc6e4154092de5898249ea623926939a968415071d74cbbda488",
        PayloadType.CREATED_AT: "2025-02-24T18:03:18.811431"
    }
}

ems_authentication_success_message = {
    PayloadType.TYPE: ControlMessageType.EMS_AUTHENTICATION_SUCCESS,
    PayloadType.PAYLOAD: {
        PayloadType.MESSAGE: "Successfully authenticated",
        PayloadType.SERIAL_NUMBER: "Sourceful-EMS",
        PayloadType.SIGNATURE: "0d253c82910f99b67c96bb960ca89729622b6d81fb8bbb5960893983aea376e4d5f84fa122889d574770ce2051fb45f8d4cd8feb3f6c54f56523fe7c0971e7f6",
        PayloadType.CREATED_AT: "2025-02-24T18:03:54.521862"
    }
}

ems_control_schedule_message = {
    PayloadType.TYPE: ControlMessageType.EMS_CONTROL_SCHEDULE,
    PayloadType.PAYLOAD: {
        PayloadType.ID: 1356,
        PayloadType.SN: "2311286262",
        PayloadType.EXECUTE_AT: "2025-03-14T15:00:00.000000",
        PayloadType.PROTOCOL: "modbus",
        PayloadType.COMMANDS: [
            {
                RegistersKey.START_REGISTER: 143,
                RegistersKey.NAME: "Max Power",
                RegistersKey.DESCRIPTION: "Maximum power for discharging electricity (Low Vol: 1W, High Vol: 10W). 470 would be 4700W or 4.7kW",
                RegistersKey.VALUE: 72
            }
        ],
        PayloadType.SERIAL_NUMBER: "Sourceful-EMS",
        PayloadType.SIGNATURE: "2a69d5eecf7c1f564e1be1e8b15711b009a66d5b8448e9b32ead40e5e741ec56294034d18212c260a5285beffcc0fef00708807e96cd296b3d0b301ddea1a45c",
        PayloadType.CREATED_AT: "2025-03-14T13:58:00.338870"
    }
}

ems_data_request_message = {
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


def test_ems_authentication_challenge_message():
    auth_challenge_message: AuthChallengeMessage = AuthChallengeMessage(ems_authentication_challenge_message)
    assert auth_challenge_message.type == ControlMessageType.EMS_AUTHENTICATION_CHALLENGE
    assert auth_challenge_message.message == "Please send authentication message"
    assert auth_challenge_message.serial_number == "Sourceful-EMS"
    assert auth_challenge_message.signature == "56f95bf2c6a0dba9de677b8328ab9fea7bda3312cf9f1fac8a6f2cbe439ddfc16f185c1e00f0cc6e4154092de5898249ea623926939a968415071d74cbbda488"
    assert auth_challenge_message.created_at == "2025-02-24T18:03:18.811431"


def test_ems_authentication_success_message():
    auth_success_message: BaseMessage = BaseMessage(ems_authentication_success_message)
    assert auth_success_message.type == ControlMessageType.EMS_AUTHENTICATION_SUCCESS
    assert auth_success_message.message == "Successfully authenticated"
    assert auth_success_message.serial_number == "Sourceful-EMS"
    assert auth_success_message.signature == "0d253c82910f99b67c96bb960ca89729622b6d81fb8bbb5960893983aea376e4d5f84fa122889d574770ce2051fb45f8d4cd8feb3f6c54f56523fe7c0971e7f6"
    assert auth_success_message.created_at == "2025-02-24T18:03:54.521862"


def test_ems_control_schedule_message():
    control_schedule_message: ControlMessage = ControlMessage(ems_control_schedule_message)
    assert control_schedule_message.type == ControlMessageType.EMS_CONTROL_SCHEDULE
    assert control_schedule_message.id == 1356
    assert control_schedule_message.sn == "2311286262"
    assert control_schedule_message.execute_at == "2025-03-14T15:00:00.000000"
    assert control_schedule_message.protocol == "modbus"

    assert len(control_schedule_message.commands) == 1

    assert control_schedule_message.serial_number == "Sourceful-EMS"
    assert control_schedule_message.signature == "2a69d5eecf7c1f564e1be1e8b15711b009a66d5b8448e9b32ead40e5e741ec56294034d18212c260a5285beffcc0fef00708807e96cd296b3d0b301ddea1a45c"
    assert control_schedule_message.created_at == "2025-03-14T13:58:00.338870"


def test_ems_data_request_message():
    data_request_message: ReadMessage = ReadMessage(ems_data_request_message)
    assert data_request_message.type == ControlMessageType.EMS_DATA_REQUEST
    assert data_request_message.id == 1356
    assert data_request_message.sn == "2311286262"
    assert data_request_message.execute_at == "2025-03-14T15:00:00.000000"
    assert data_request_message.protocol == "modbus"

    assert len(data_request_message.commands) == 1

    assert data_request_message.serial_number == "Sourceful-EMS"
    assert data_request_message.signature == "2a69d5eecf7c1f564e1be1e8b15711b009a66d5b8448e9b32ead40e5e741ec56294034d18212c260a5285beffcc0fef00708807e96cd296b3d0b301ddea1a45c"
    assert data_request_message.created_at == "2025-03-14T13:58:00.338870"
