from typing import List, Dict, Any
from server.devices.common.types import ModbusProtocol
from server.devices.registerValue import RegisterValue
import logging
from server.web.socket.control.control_objects.types import PayloadType
from server.web.socket.control.control_objects.base_message import BaseMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Command:
    def __init__(self, data: Dict[str, Any]):
        self.register: int = data['register']
        self.type: str = data['type']
        self.datatype: str = data['datatype']
        self.unit: str = data['unit']
        self.scaling_factor: float = data['scaling_factor']
        self.description: str = data['description']
        self.value: float = data['value']


class ControlMessage(BaseMessage):
    def __init__(self, data: dict):
        super().__init__(data)
        self.sn: str = self.payload.get(PayloadType.SN)
        self.execute_at = self.payload.get(PayloadType.EXECUTE_AT)
        self.protocol: str = self.payload.get(PayloadType.PROTOCOL)
        self.retries: int = self.payload.get(PayloadType.RETRIES)
        self.commands: List[Command] = [Command(cmd) for cmd in self.payload.get(PayloadType.COMMANDS, [])]

        # Log as dictionary
        logger.info(f"Initialized control message: {self.id}")

    def execute(self, device: ModbusProtocol) -> List[bool]:
        try:
            logger.info(f"Executing control message: {self}")

            for command in self.commands:
                address = command.register
                value = command.value
                logger.info(f"Writing value {value} to address {address}")
                RegisterValue.write_single(device=device, address=address, value=value)

                logger.info(f"Wrote value {value} to address {address}")

        except Exception as e:
            logger.error(f"Error executing control message: {e}")
            return [False]
