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
    SOLARMAN_V5 = 'solarmanv5'
    SUNSPEC = 'sunspec'
    REST_API = 'rest_api'


class RegistersKey(Enum):
    FCODE = 'fcode'
    START_REGISTER = 'start_register'
    NUM_OF_REGISTERS = 'num_of_registers'


class OperationKey(Enum):
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04


class DeviceCategory(Enum):
    INVERTERS = 'inverters'
    METERS = 'meters'
    


    
    
    
