from server.web.socket.control.control_objects.base_message import BaseMessage
from server.web.socket.control.control_objects.types import PayloadType


class AuthChallengeMessage(BaseMessage):
    def __init__(self, data: dict):
        super().__init__(data)
