from enum import Enum


class ControlMessageType(str, Enum):

    # General
    INIT = "init"

    # Outgoing message types
    DEVICE_AUTHENTICATE = "device_authenticate"
    DEVICE_CONTROL_SCHEDULE_ACK = "device_control_schedule_ack"
    DEVICE_CONTROL_SCHEDULE_NACK = "device_control_schedule_nack"

    # Incoming message types
    EMS_AUTHENTICATION_ERROR = "ems_authentication_error"
    EMS_AUTHENTICATION_SUCCESS = "ems_authentication_success"
    EMS_AUTHENTICATION_TIMEOUT = "ems_authentication_timeout"
    EMS_AUTHENTICATION_CHALLENGE = "ems_authentication_challenge"
    EMS_CONTROL_SCHEDULE = "ems_control_schedule"


class PayloadType(str, Enum):
    DEVICE_NAME = "deviceName"
    SERIAL_NUMBER = "serialNumber"
    SIGNATURE = "signature"
    CREATED_AT = "created_at"
    TYPE = "type"
    PAYLOAD = "payload"
    RETRIES = "retrys"
    REASON = "reason"
    MESSAGE = "message"

    ID = "id"
    SN = "sn"
    EXECUTE_AT = "execute_at"
    PROTOCOL = "protocol"
    COMMANDS = "commands"
