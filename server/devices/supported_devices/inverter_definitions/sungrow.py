from ...profile_keys import (
    ProtocolKey,
    ProfileKey,
    RegistersKey,
    FunctionCodeKey,
    DataTypeKey,
    EndiannessKey,
)
from ..profile import ModbusProfile
from ...common.types import ModbusDevice


class SungrowProfile(ModbusProfile):
    def __init__(self):
        super().__init__(sungrow_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return True


sungrow_profile = {
    ProfileKey.NAME: "sungrow",
    ProfileKey.MAKER: "Sungrow",
    ProfileKey.VERSION: "V1.1b3",
    ProfileKey.VERBOSE_ALWAYS: False,
    ProfileKey.DISPLAY_NAME: "Sungrow",
    ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
    ProfileKey.DESCRIPTION: "Another inverter profile...",
    ProfileKey.SN: {
        RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
        RegistersKey.START_REGISTER: 4989,
        RegistersKey.NUM_OF_REGISTERS: 10,
        RegistersKey.DATA_TYPE: DataTypeKey.STR,
        RegistersKey.UNIT: "",
        RegistersKey.DESCRIPTION: "Serial number",
        RegistersKey.SCALE_FACTOR: 1,
        RegistersKey.ENDIANNESS: EndiannessKey.BIG,
    },
    ProfileKey.ALWAYS_INCLUDE: [],
    ProfileKey.REGISTERS_VERBOSE: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 4949,
            RegistersKey.NUM_OF_REGISTERS: 87,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5213,
            RegistersKey.NUM_OF_REGISTERS: 28,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5602,
            RegistersKey.NUM_OF_REGISTERS: 36,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6099,
            RegistersKey.NUM_OF_REGISTERS: 96,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6195,
            RegistersKey.NUM_OF_REGISTERS: 94,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6289,
            RegistersKey.NUM_OF_REGISTERS: 96,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6385,
            RegistersKey.NUM_OF_REGISTERS: 83,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6468,
            RegistersKey.NUM_OF_REGISTERS: 96,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6564,
            RegistersKey.NUM_OF_REGISTERS: 83,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6647,
            RegistersKey.NUM_OF_REGISTERS: 96,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6743,
            RegistersKey.NUM_OF_REGISTERS: 83,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 12999,
            RegistersKey.NUM_OF_REGISTERS: 119,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 13049,
            RegistersKey.NUM_OF_REGISTERS: 51,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 33041,
            RegistersKey.NUM_OF_REGISTERS: 7,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 33147,
            RegistersKey.NUM_OF_REGISTERS: 1,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 31221,
            RegistersKey.NUM_OF_REGISTERS: 1,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 33207,
            RegistersKey.NUM_OF_REGISTERS: 2,
        },
    ],
    ProfileKey.REGISTERS: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5035,
            RegistersKey.NUM_OF_REGISTERS: 1,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "Hz",
            RegistersKey.DESCRIPTION: "Grid frequency",
            RegistersKey.SCALE_FACTOR: 0.1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5016,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.U32,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "DC Power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
        {
            RegistersKey.NAME: "Total Active Power",
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 13033,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.I32,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "Total active power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
        },
        {
            RegistersKey.NAME: "Battery Power",
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 13021,
            RegistersKey.NUM_OF_REGISTERS: 1,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "Battery power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
    ],
    ProfileKey.KEYWORDS: ["sungrow", "Espressif"],
}
