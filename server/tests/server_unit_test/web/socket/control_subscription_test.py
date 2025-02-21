from server.web.socket.control.control_subscription import ControlSubscription
from server.web.socket.control.control_objects.control_message import ControlMessage
from server.app.blackboard import BlackBoard
from unittest.mock import Mock
import pytest
from server.web.socket.control.control_objects.types import PayloadType, ControlMessageType


@pytest.fixture
def control_message():
    obj = {
        PayloadType.TYPE: ControlMessageType.EMS_CONTROL_SCHEDULE,
        PayloadType.PAYLOAD: {
            PayloadType.ID: "f42ea576ac87184445",
            PayloadType.SN: "8383jsj238js",
            PayloadType.EXECUTE_AT: "2025-02-21T18:53:48.3529926Z",
            PayloadType.PROTOCOL: "modbus",
            PayloadType.RETRIES: 0,
            PayloadType.COMMANDS: [
                {
                    "register": 1,
                    "type": "ControlMessagePayload",
                    "datatype": "float32",
                    "unit": "kW",
                    "scaling_factor": 0.1,
                    "description": "Fiddle stuff",
                    "value": 1337
                }
            ],
            PayloadType.SERIAL_NUMBER: "Sourceful-EMS",
            PayloadType.SIGNATURE: "657909c419915146dc2736ffe406184ccce02bd1f70f933b80ce8d4bcb4ffd0409b4c4f929a4434b0f1a9bc95953e36ce979df9b306eed9c4e4e9c238403c802",
            PayloadType.CREATED_AT: "2025-02-21T18:53:48.3529925Z"
        }
    }
    return ControlMessage(obj)


def test_validate_message_signature(control_message):
    control_subscription_obj = ControlSubscription(Mock(spec=BlackBoard), "ws://example.com")
    assert control_subscription_obj._verify_message_signature(control_message)
