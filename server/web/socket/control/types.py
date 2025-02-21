from enum import Enum


class ControlMessageType(str, Enum):
    INIT = "init"
    EMS_AUTHENTICATION_CHALLENGE = "ems_authentication_challenge"
    DEVICE_AUTHENTICATE = "device_authenticate"
    EMS_AUTHENTICATION_SUCCESS = "ems_authentication_success"
    EMS_AUTHENTICATION_ERROR = "ems_authentication_error"
    EMS_CONTROL_SCHEDULE = "ems_control_schedule"


class PayloadType(str, Enum):
    DEVICE_NAME = "deviceName"
    SERIAL_NUMBER = "serialNumber"
    SIGNATURE = "signature"
    CREATED_AT = "created_at"
    TYPE = "type"
    PAYLOAD = "payload"

    ID = "id"
    SN = "sn"
    EXECUTE_AT = "execute_at"
    PROTOCOL = "protocol"
    RETRYS = "retrys"
    COMMANDS = "commands"
