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


class Sdm630Profile(ModbusProfile):
    def __init__(self):
        super().__init__(sdm630_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return True


sdm630_profile = {
    ProfileKey.NAME: "sdm630",
    ProfileKey.MAKER: "Eastron",
    ProfileKey.VERSION: "V1.1b3",
    ProfileKey.VERBOSE_ALWAYS: False,
    ProfileKey.DISPLAY_NAME: "SDM630",
    ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
    ProfileKey.DESCRIPTION: "Another meter profile...",
    ProfileKey.SN: {
        RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
        RegistersKey.START_REGISTER: 64512,
        RegistersKey.NUM_OF_REGISTERS: 2,
        RegistersKey.DATA_TYPE: DataTypeKey.U32,
        RegistersKey.UNIT: "",
        RegistersKey.DESCRIPTION: "Serial number",
        RegistersKey.SCALE_FACTOR: 1,
        RegistersKey.ENDIANNESS: EndiannessKey.BIG,
    },
    ProfileKey.ALWAYS_INCLUDE: [],
    ProfileKey.REGISTERS_VERBOSE: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 0,
            RegistersKey.NUM_OF_REGISTERS: 100,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 100,
            RegistersKey.NUM_OF_REGISTERS: 100,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 200,
            RegistersKey.NUM_OF_REGISTERS: 100,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 300,
            RegistersKey.NUM_OF_REGISTERS: 100,
        },
    ],
    ProfileKey.REGISTERS: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 12,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.F32,
            RegistersKey.UNIT: "kW",
            RegistersKey.DESCRIPTION: "Phase 1 power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 14,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.F32,
            RegistersKey.UNIT: "kW",
            RegistersKey.DESCRIPTION: "Phase 2 power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 16,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.F32,
            RegistersKey.UNIT: "kW",
            RegistersKey.DESCRIPTION: "Phase 3 power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 52,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.F32,
            RegistersKey.UNIT: "kW",
            RegistersKey.DESCRIPTION: "Total system power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 62,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.F32,
            RegistersKey.UNIT: "",
            RegistersKey.DESCRIPTION: "Power direction (negative = exporting)",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 70,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.F32,
            RegistersKey.UNIT: "Hz",
            RegistersKey.DESCRIPTION: "Grid frequency",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 72,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.F32,
            RegistersKey.UNIT: "kWh",
            RegistersKey.DESCRIPTION: "Total import energy",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 74,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.F32,
            RegistersKey.UNIT: "kWh",
            RegistersKey.DESCRIPTION: "Total export energy",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
        },
    ],
    ProfileKey.KEYWORDS: ["sdm630"],
}
