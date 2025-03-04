from server.web.socket.control.control_messages.base_message import BaseMessage
from server.web.socket.control.control_messages.auth_challenge_message import AuthChallengeMessage
from server.web.socket.control.control_messages.control_message import ControlMessage
from server.web.socket.control.control_messages.types import ControlMessageType


ems_authentication_challenge_message = {
    "type": "ems_authentication_challenge",
    "payload": {
        "message": "Please send authentication message",
        "serialNumber": "Sourceful-EMS",
        "signature": "56f95bf2c6a0dba9de677b8328ab9fea7bda3312cf9f1fac8a6f2cbe439ddfc16f185c1e00f0cc6e4154092de5898249ea623926939a968415071d74cbbda488",
        "created_at": "2025-02-24T18:03:18.811431"
    }
}

ems_authentication_success_message = {
    "type": "ems_authentication_success",
    "payload": {
        "message": "Successfully authenticated",
        "serialNumber": "Sourceful-EMS",
        "signature": "0d253c82910f99b67c96bb960ca89729622b6d81fb8bbb5960893983aea376e4d5f84fa122889d574770ce2051fb45f8d4cd8feb3f6c54f56523fe7c0971e7f6",
        "created_at": "2025-02-24T18:03:54.521862"
    }
}

ems_control_schedule_message = {
    "type": "ems_control_schedule",
    "payload": {
        "id": "controlId",
        "sn": "DEADBEEF",
            "execute_at": "2025-02-24T18:29:59.172301",
            "protocol": "modbus",
            "retrys": 0,
            "commands": [
                {
                    "register": 1,
                    "type": "ControlMessagePayload",
                    "datatype": "float32",
                    "unit": "kW",
                    "scaling_factor": 0.1,
                    "description": "Fiddle stuff",
                    "value": 5000
                }
            ],
        "serialNumber": "Sourceful-EMS",
        "signature": "fe697235a6d60dd53ed84ab2c6bec6ee5e843ecdddb2689204bc2359c25056cbfb5c41261179acc739d9bf687a76f49bf7c0db8fe8bd601ef3cb6663a3ea6c45",
        "created_at": "2025-02-24T18:01:43.172301"
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
    assert control_schedule_message.id == None
    assert control_schedule_message.sn == "DEADBEEF"
    assert control_schedule_message.execute_at == "2025-02-24T18:29:59.172301"
    assert control_schedule_message.protocol == "modbus"
    assert control_schedule_message.retries == 0

    assert len(control_schedule_message.commands) == 1

    assert control_schedule_message.serial_number == "Sourceful-EMS"
    assert control_schedule_message.signature == "fe697235a6d60dd53ed84ab2c6bec6ee5e843ecdddb2689204bc2359c25056cbfb5c41261179acc739d9bf687a76f49bf7c0db8fe8bd601ef3cb6663a3ea6c45"
    assert control_schedule_message.created_at == "2025-02-24T18:01:43.172301"
