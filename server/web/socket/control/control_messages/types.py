from enum import Enum


class ControlMessageType(str, Enum):

    # General
    INIT = "init"

    # Outgoing message types
    DEVICE_AUTHENTICATE = "device_authenticate"
    DEVICE_CONTROL_SCHEDULE_ACK = "device_control_schedule_ack"
    DEVICE_CONTROL_SCHEDULE_NACK = "device_control_schedule_nack"
    DEVICE_CONTROL_CANCEL_SCHEDULE_ACK = "device_control_cancel_schedule_ack"
    DEVICE_CONTROL_SCHEDULE_DONE = "device_control_schedule_done"
    DEVICE_DATA_RESPONSE = "device_data_response"

    # Incoming message types
    EMS_AUTHENTICATION_ERROR = "ems_authentication_error"
    EMS_AUTHENTICATION_SUCCESS = "ems_authentication_success"
    EMS_AUTHENTICATION_TIMEOUT = "ems_authentication_timeout"
    EMS_AUTHENTICATION_CHALLENGE = "ems_authentication_challenge"
    EMS_CONTROL_SCHEDULE = "ems_control_schedule"
    EMS_CONTROL_SCHEDULE_CANCEL = "ems_control_schedule_cancel"
    EMS_DATA_REQUEST = "ems_data_request"
    EMS_PRE_SETUP = "ems_pre_setup"
    


class PayloadType(str, Enum):
    DEVICE_NAME = "deviceName"
    SERIAL_NUMBER = "serialNumber"
    SIGNATURE = "signature"
    CREATED_AT = "created_at"
    TYPE = "type"
    PAYLOAD = "payload"
    RETRIES = "retries"
    REASON = "reason"
    MESSAGE = "message"
    DATA = "data"

    ID = "id"
    SN = "sn"
    EXECUTE_AT = "execute_at"
    PROTOCOL = "protocol"
    COMMANDS = "commands"
    ACTION = "action"

    
# {\"power\": 1830, \"actionType\": \"battery.discharge\"}
class PayloadAction(str, Enum):
    NONE = "none",
    TYPE = "actionType",
    POWER = "power"

class PayloadActionType(str, Enum):
    NONE = "none",
    BATTERY_DISCHARGE = "battery.discharge"
    BATTERY_CHARGE = "battery.charge"
