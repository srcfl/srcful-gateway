from typing import List, Dict, Any
from server.web.socket.control.control_messages.modbus_message import ModbusMessage, ModbusCommand
from server.web.socket.control.control_messages.types import PayloadType
from server.devices.common.types import ModbusProtocol
from server.devices.registerValue import RegisterValue
from server.devices.profile_keys import RegistersKey
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Command(ModbusCommand):
    # Required fields
    REQUIRED_FIELDS = {RegistersKey.START_REGISTER, RegistersKey.NUM_OF_REGISTERS}

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

        missing_fields = self.REQUIRED_FIELDS - data.keys()
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        # Required fields
        self.register: int = data[RegistersKey.START_REGISTER]
        self.function_code: str = data[RegistersKey.FUNCTION_CODE]
        self.num_of_registers: int = data[RegistersKey.NUM_OF_REGISTERS]

        # Optional fields with defaults
        self.data_type: str = data[RegistersKey.DATA_TYPE]
        self.scale_factor: float = data[RegistersKey.SCALE_FACTOR]
        self.endianness: str = data[RegistersKey.ENDIANNESS]
        self.value: float = data.get('value', 0)  # Optional, only updated if the command is executed


class ReadMessage(ModbusMessage):
    def __init__(self, data: dict):
        super().__init__(data)
        self.commands: List[Command] = [Command(cmd) for cmd in self.payload.get(PayloadType.COMMANDS, [])]

        logger.debug(f"Initialized read message: {self.id}")

    def process_commands(self, device: ModbusProtocol):

        logger.info(f"Processing commands: {self.commands}")

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

                command.success = len(raw) > 0  # 0 bytes means the read was not successful

                logger.info(f"Read value {value} from address {address}")
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error processing commands: {e}")
