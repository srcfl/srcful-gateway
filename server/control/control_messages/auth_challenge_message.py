from server.control.control_messages.base_message import BaseMessage
from server.control.control_messages.types import PayloadType


class AuthChallengeMessage(BaseMessage):
    def __init__(self, data: dict):
        super().__init__(data)
