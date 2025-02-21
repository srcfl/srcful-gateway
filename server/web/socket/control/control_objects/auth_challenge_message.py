from server.web.socket.control.control_objects.base_message import BaseMessage


class AuthChallengeMessage(BaseMessage):
    def __init__(self, data: dict):
        super().__init__(data)
