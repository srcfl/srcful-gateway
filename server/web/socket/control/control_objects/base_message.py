from server.web.socket.control.control_objects.types import PayloadType


class BaseMessage:
    def __init__(self, data: dict):
        # Common header fields
        self.id: str | None = data.get(PayloadType.ID, None)
        self.type: str = data.get(PayloadType.TYPE)
        self.payload: str = data.get(PayloadType.PAYLOAD)

        # Common payload fields
        self.serial_number: str = self.payload.get(PayloadType.SERIAL_NUMBER)
        self.signature: str = self.payload.get(PayloadType.SIGNATURE)
        self.created_at: str = self.payload.get(PayloadType.CREATED_AT)
        self.message: str | None = self.payload.get(PayloadType.MESSAGE)
