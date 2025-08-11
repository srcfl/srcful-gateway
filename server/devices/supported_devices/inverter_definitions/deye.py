from ...profile_keys import (
    ProtocolKey,
    ProfileKey,
    RegistersKey,
    FunctionCodeKey,
    DeviceCategoryKey,
    DataTypeKey,
    EndiannessKey,
)
from ..profile import ModbusProfile
from ...common.types import ModbusDevice


class DeyeProfile(ModbusProfile):
    def __init__(self):
        super().__init__(deye_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return True


deye_profile = {
    ProfileKey.NAME: "deye",
    ProfileKey.MAKER: "Deye",
    ProfileKey.VERSION: "V1.1b3",
    ProfileKey.VERBOSE_ALWAYS: False,
    ProfileKey.DISPLAY_NAME: "Deye",
    ProfileKey.PROTOCOL: ProtocolKey.SOLARMAN,
    ProfileKey.DESCRIPTION: "Another inverter profile...",
    ProfileKey.SN: {
        RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
        RegistersKey.START_REGISTER: 3,
        RegistersKey.NUM_OF_REGISTERS: 8,
        RegistersKey.DATA_TYPE: DataTypeKey.STR,
        RegistersKey.UNIT: "",
        RegistersKey.DESCRIPTION: "Serial number",
        RegistersKey.SCALE_FACTOR: 1,
        RegistersKey.ENDIANNESS: EndiannessKey.BIG,
    },
    ProfileKey.ALWAYS_INCLUDE: [0],
    ProfileKey.REGISTERS_VERBOSE: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 0,
            RegistersKey.NUM_OF_REGISTERS: 59,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 60,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 185,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 310,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 435,
            RegistersKey.NUM_OF_REGISTERS: 64,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 500,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 625,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
    ],
    ProfileKey.REGISTERS: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 609,
            RegistersKey.NUM_OF_REGISTERS: 1,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "Hz",
            RegistersKey.DESCRIPTION: "Grid frequency",
            RegistersKey.SCALE_FACTOR: 0.01,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 672,
            RegistersKey.NUM_OF_REGISTERS: 4,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "DC Power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
    ],
    ProfileKey.KEYWORDS: ["deye", "high-flying"],
}
