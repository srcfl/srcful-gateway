from enum import Enum


class ProfileKey(Enum):
    NAME = 'name'
    VERSION = 'version'
    VERBOSE_ALWAYS = 'verbose_always'
    MODEL_GROUP = 'model_group'
    DISPLAY_NAME = 'display_name'
    PROTOCOL = 'protocol'
    DESCRIPTION = 'description'
    REGISTERS_VERBOSE = 'registers_verbose'
    REGISTERS = 'registers'
    BASE_URL = 'base_url'
    ENDPOINTS = 'endpoints'


class ProtocolKey(Enum):
    MODBUS = 'modbus'
    SOLARMAN = 'solarman'
    SUNSPEC = 'sunspec'
    REST = 'rest'


class RegistersKey(Enum):
    FCODE = 'fcode'
    START_REGISTER = 'start_register'
    NUM_OF_REGISTERS = 'num_of_registers'
    DATA_TYPE = 'data_type'
    UNIT = 'unit'
    DESCRIPTION = 'description'
    SCALE_FACTOR = 'scale_factor'


class DataType(Enum):
    U16 = 'U16'    # Unsigned 16-bit integer
    I16 = 'I16'    # Signed 16-bit integer
    U32 = 'U32'    # Unsigned 32-bit integer
    I32 = 'I32'    # Signed 32-bit integer
    F32 = 'F32'    # 32-bit floating point
    STR = 'STR'    # String


class OperationKey(Enum):
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04


class DeviceCategory(Enum):
    INVERTERS = 'inverters'
    METERS = 'meters'
    


    
    
    
