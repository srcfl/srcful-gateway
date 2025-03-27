from typing import List, Dict, Any
from server.devices.common.types import ModbusProtocol
from server.devices.registerValue import RegisterValue
from server.web.socket.control.control_messages.modbus_message import ModbusMessage
from server.web.socket.control.control_messages.types import PayloadType
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command:
    def __init__(self, data: Dict[str, Any]):
        self.register: int = data['register']
        self.name: str = data['name']
        self.description: str = data['description']
        self.value: float = data['value']
        self.success: bool = False  # Optional, only used if the command is executed


class ControlMessage(ModbusMessage):
    def __init__(self, data: dict):
        super().__init__(data)
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
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error executing control message: {e}")
