from enum import Enum

class InverterKey(Enum):
    HUAWEI = 'Huawei'
    SUNGROW = 'Sungrow'
    SUNGROW_HYBRID = 'Sungrow Hybrid'
    GOODWE = 'Goodwe'
    SOLAREDGE = "SolarEdge"
    FERROAMP = "FerroAmp"
    SOLIS = "Solis"
    GROWATT = "Growatt"
    FRONIUS = "Fronius"
    FOXESS = "FoxEss"
    LQT40S = "lqt40s"
    DEYE = "Deye"
    DEYE_HYBRID = "Deye Hybrid"
    SMA = "SMA"


class ProfileKey(Enum):
    NAME = 'name'
    DISPLAY_NAME = 'display_name'
    REGISTERS = 'registers'
    PROTOCOL = 'protocol'


class ProtocolKey(Enum):
    MODBUS = 'modbus'
    SOLARMAN_V5 = 'solarmanv5'

class RegistersKey(Enum):
    OPERATION = 'operation'
    START_REGISTER = 'start_register'
    NUM_OF_REGISTERS = 'num_of_registers'


class OperationKey(Enum):
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04
