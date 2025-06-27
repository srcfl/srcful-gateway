from enum import Enum


class ProfileKey(str, Enum):
    NAME = 'name'
    SN = 'sn'
    MAKER = 'maker'
    VERSION = 'version'
    VERBOSE_ALWAYS = 'verbose_always'
    MODEL_GROUP = 'model_group'
    DISPLAY_NAME = 'display_name'
    PROTOCOL = 'protocol'
    DESCRIPTION = 'description'
    REGISTERS_VERBOSE = 'registers_verbose'
    REGISTERS = 'registers'
    ALL_REGISTERS = 'all_registers'
    BASE_URL = 'base_url'
    ENDPOINTS = 'endpoints'
    KEYWORDS = 'keywords'
    ALWAYS_INCLUDE = 'always_include'
    CONDITIONS = 'conditions'


class ProtocolKey(str, Enum):
    MODBUS = 'modbus'
    SOLARMAN = 'solarman'
    SUNSPEC = 'sunspec'
    REST = 'rest'


class RegistersKey(str, Enum):
    NAME = 'name'
    FUNCTION_CODE = 'function_code'
    START_REGISTER = 'start_register'
    NUM_OF_REGISTERS = 'num_of_registers'
    DATA_TYPE = 'data_type'
    UNIT = 'unit'
    DESCRIPTION = 'description'
    SCALE_FACTOR = 'scale_factor'
    ENDIANNESS = 'endianness'
    SCALE_FACTOR_REGISTER = 'scale_factor_register'
    VALUE = 'value'


class DataTypeKey(str, Enum):
    U16 = 'U16'    # Unsigned 16-bit integer
    I16 = 'I16'    # Signed 16-bit integer
    U32 = 'U32'    # Unsigned 32-bit integer
    I32 = 'I32'    # Signed 32-bit integer
    F32 = 'F32'    # 32-bit floating point
    U64 = 'U64'    # Unsigned 64-bit integer
    I64 = 'I64'    # Signed 64-bit integer
    STR = 'STR'    # String


class EndiannessKey(str, Enum):
    BIG = 'big'
    LITTLE = 'little'


class FunctionCodeKey(int, Enum):
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04
    WRITE_MULTIPLE_REGISTERS = 0x10


class DeviceCategoryKey(str, Enum):
    INVERTERS = 'inverters'
    METERS = 'meters'


class ConditionTypeKey(str, Enum):
    REGISTER_VALUE_RANGE = 'register_value_range'
    REGISTER_VALUE_EQUALS = 'register_value_equals'
    REGISTER_VALUE_NOT_EQUALS = 'register_value_not_equals'
    REGISTER_VALUE_GREATER_THAN = 'register_value_greater_than'
    REGISTER_VALUE_LESS_THAN = 'register_value_less_than'
    REGISTER_READABLE = 'register_readable'


class ConditionKey(str, Enum):
    TYPE = 'type'
    REGISTER = 'register'
    VALUE = 'value'
    MIN_VALUE = 'min_value'
    MAX_VALUE = 'max_value'
    DESCRIPTION = 'description'
