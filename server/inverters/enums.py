from enum import Enum


class ProfileKey(Enum):
    NAME = 'name'
    DISPLAY_NAME = 'display_name'
    REGISTERS_VERBOSE = 'registers_verbose'
    REGISTERS = 'registers'
    PROTOCOL = 'protocol'


class ProtocolKey(Enum):
    MODBUS = 'modbus'
    SOLARMAN_V5 = 'solarmanv5'

class RegistersKey(Enum):
    FCODE = 'fcode'
    START_REGISTER = 'start_register'
    NUM_OF_REGISTERS = 'num_of_registers'


class OperationKey(Enum):
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04
