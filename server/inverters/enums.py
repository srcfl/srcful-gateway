from enum import Enum

class ProfileKey(Enum):
    NAME = 'name'
    REGISTERS = 'registers'


class RegistersKey(Enum):
    OPERATION = 'operation'
    START_REGISTER = 'start_register'
    NUM_OF_REGISTERS = 'num_of_registers'


class OperationKey(Enum):
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04