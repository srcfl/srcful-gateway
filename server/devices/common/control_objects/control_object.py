from datetime import datetime
from typing import List, Dict, Any
from server.devices.common.types import ModbusProtocol
from server.devices.registerValue import RegisterValue
import logging

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


class ControlObject:
    def __init__(self, data: dict):
        payload = data.get('payload', data)  # Handle both full JSON and direct payload
        self.id: str = payload['id']
        self.sn: str = payload['sn']
        self.signature: str = payload['signature']
        self.created_at: datetime = datetime.strptime(
            payload['created_at'], '%Y-%m-%d %H:%M:%S')
        self.execute_at: datetime = datetime.strptime(
            payload['execute_at'], '%Y-%m-%d %H:%M:%S')
        self.protocol: str = payload['protocol']
        self.commands: List[Command] = [Command(cmd) for cmd in payload['commands']]

        logger.info(f"Control object initialized: {self}")

    def execute(self, device: ModbusProtocol) -> List[bool]:
        try:
            logger.info(f"Executing control object: {self}")

            for command in self.commands:
                address = command.register
                value = command.value
                logger.info(f"Writing value {value} to address {address}")
                RegisterValue.write_single(device=device, address=address, value=value)

                logger.info(f"Wrote value {value} to address {address}")

        except Exception as e:
            logger.error(f"Error executing control object: {e}")
            return [False]
