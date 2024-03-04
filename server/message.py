class Message:
    class Type(Enum):
        Error = "error"
        Warning = "warning"
        Info = "info"

    def __init__(self, message: str, type: Type, timestamp, id):
        self.message = message
        self.type = type
        self.timestamp = timestamp
        self.id = id