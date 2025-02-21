from server.web.socket.control.control_objects.types import PayloadType


class BaseMessage:
    def __init__(self, data: dict):
        # Common header fields
        self.type = data.get(PayloadType.TYPE)
        self.payload = data.get(PayloadType.PAYLOAD)

        # Common payload fields
        self.serial_number = self.payload.get(PayloadType.SERIAL_NUMBER)
        self.signature = self.payload.get(PayloadType.SIGNATURE)
        self.created_at = self.payload.get(PayloadType.CREATED_AT)
