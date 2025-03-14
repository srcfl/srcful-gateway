from typing import List, Dict, Any
from server.devices.common.types import ModbusProtocol
from server.devices.registerValue import RegisterValue
import logging
from server.web.socket.control.control_messages.types import PayloadType
from server.web.socket.control.control_messages.base_message import BaseMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command:
    def __init__(self, data: Dict[str, Any]):
        self.register: int = data['register']
        self.name: str = data['name']
        self.description: str = data['description']
        self.value: float = data['value']
        self.success: bool = False  # Optional, only used if the command is executed


class ControlMessage(BaseMessage):
    def __init__(self, data: dict):
        super().__init__(data)
        self.sn: str = self.payload.get(PayloadType.SN)
        self.execute_at = self.payload.get(PayloadType.EXECUTE_AT)
        self.protocol: str = self.payload.get(PayloadType.PROTOCOL)
        self.retries: int = self.payload.get(PayloadType.RETRIES)
        self.commands: List[Command] = [Command(cmd) for cmd in self.payload.get(PayloadType.COMMANDS, [])]

        logger.debug(f"Initialized control message: {self.id}")

    def process_commands(self, device: ModbusProtocol):
        try:
            for command in self.commands:
                address = command.register
                value = command.value

                logger.debug(f"Writing value {value} to address {address}")

                res = RegisterValue.write_single(device=device, address=address, value=value)
                command.success = res

                logger.debug(f"Wrote value {value} to address {address}")

        except Exception as e:
            logger.error(f"Error executing control message: {e}")

        finally:
            # We return the control message object with the updated success status in each command
            return self
