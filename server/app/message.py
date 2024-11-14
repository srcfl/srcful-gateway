from enum import Enum


class Message:
    class Type(Enum):
        Error = "error"
        Warning = "warning"
        Info = "info"

    def __init__(self, message: str, type: 'Message.Type', seconds:int, id:int):
        self._message = message
        self._type = type
        self._timestamp = seconds
        self._id = id

    @property
    def message(self) -> str:
        return self._message

    @property
    def type(self) -> 'Message.Type':
        return self._type

    @property
    def timestamp(self) -> int:
        return self._timestamp
    
    @timestamp.setter
    def timestamp(self, seconds: int):
        self._timestamp = seconds

    @property
    def id(self) -> int:
        return self._id
