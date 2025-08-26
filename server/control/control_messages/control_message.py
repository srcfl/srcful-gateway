from typing import List, Dict, Any
from server.devices.common.types import ModbusDevice
from server.devices.registerValue import RegisterValue
from server.control.control_messages.modbus_message import ModbusMessage, ModbusCommand
from server.control.control_messages.types import PayloadType
from server.devices.profile_keys import RegistersKey
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(ModbusCommand):

    REQUIRED_FIELDS = {RegistersKey.START_REGISTER, RegistersKey.VALUE}

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

        missing_fields = self.REQUIRED_FIELDS - data.keys()
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        # Required fields
        self.register: int = data[RegistersKey.START_REGISTER]
        self.value: float = data[RegistersKey.VALUE]


class ControlMessage(ModbusMessage):
    def __init__(self, data: dict):
        super().__init__(data)
        self.commands: List[Command] = [Command(cmd) for cmd in self.payload.get(PayloadType.COMMANDS, [])]

        logger.debug(f"Initialized control message: {self.id}")

    def process_commands(self, device: ModbusDevice):
        try:
            for command in self.commands:
                address = command.register
                value = command.value

                logger.debug(f"Writing value {value} to address {address}")

                command.success = RegisterValue.write_single(device=device, address=address, value=value)

                logger.debug(f"Wrote value {value} to address {address}")

                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error executing control message: {e}")
