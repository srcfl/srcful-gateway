from server.web.socket.control.control_messages.base_message import BaseMessage
from server.web.socket.control.control_messages.types import PayloadType
from server.devices.common.types import ModbusProtocol


class ModbusMessage(BaseMessage):
    def __init__(self, data: dict):
        super().__init__(data)
        self.sn: str = self.payload.get(PayloadType.SN)
        self.execute_at = self.payload.get(PayloadType.EXECUTE_AT)
        self.protocol: str = self.payload.get(PayloadType.PROTOCOL)

    def process_commands(self, device: ModbusProtocol):
        raise NotImplementedError("This method should be implemented by the subclass")
