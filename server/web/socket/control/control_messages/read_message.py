from typing import List, Dict, Any
from server.web.socket.control.control_messages.modbus_message import ModbusMessage
from server.web.socket.control.control_messages.types import PayloadType
from server.devices.common.types import ModbusProtocol
from server.devices.registerValue import RegisterValue
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Command:
    # Required fields
    REQUIRED_FIELDS = {'register', 'function_code', 'num_of_registers', 'data_type'}

    def __init__(self, data: Dict[str, Any]):

        missing_fields = self.REQUIRED_FIELDS - data.keys()
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        # Required fields
        self.register: int = data['register']
        self.function_code: str = data['function_code']
        self.num_of_registers: int = data['num_of_registers']
        self.data_type: str = data['data_type']

        # Optional fields with defaults
        self.name: str = data.get('name', '')
        self.description: str = data.get('description', '')
        self.scale_factor: float = data.get('scale_factor', 1.0)
        self.endianness: str = data.get('endianness', 'big')
        self.value: float = data.get('value', 0)  # Optional, only updated if the command is executed


class ReadMessage(ModbusMessage):
    def __init__(self, data: dict):
        super().__init__(data)
        self.commands: List[Command] = [Command(cmd) for cmd in self.payload.get(PayloadType.COMMANDS, [])]

        logger.debug(f"Initialized read message: {self.id}")

    def process_commands(self, device: ModbusProtocol):
        try:
            for command in self.commands:
                address = command.register
                num_of_registers = command.num_of_registers
                function_code = command.function_code
                data_type = command.data_type
                scale_factor = command.scale_factor
                endianness = command.endianness

                reg = RegisterValue(address=address,
                                    size=num_of_registers,
                                    function_code=function_code,
                                    data_type=data_type,
                                    scale_factor=scale_factor,
                                    endianness=endianness)

                raw, swapped, value = reg.read_value(device=device)
                command.value = value

                logger.info(f"Read value {value} from address {address}")
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error processing commands: {e}")
