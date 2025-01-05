from ..profile_keys import (
    ProtocolKey,
    ProfileKey,
    RegistersKey,
    FunctionCodeKey,
    DeviceCategoryKey,
    DataTypeKey,
    EndiannessKey,
)

supported_devices = {
    DeviceCategoryKey.INVERTERS: [
        {
            ProfileKey.NAME: "huawei",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Huawei",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 30000,
                    RegistersKey.NUM_OF_REGISTERS: 125,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 32000,
                    RegistersKey.NUM_OF_REGISTERS: 125,
                },
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 32085,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 32064,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.I32,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "DC Power",
                    RegistersKey.SCALE_FACTOR: 0.001,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["huawei", "sun2000"],
        },
        {
            ProfileKey.NAME: "solaredge",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "SolarEdge",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "SolarEdge inverter profile",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40000,
                    RegistersKey.NUM_OF_REGISTERS: 69,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40069,
                    RegistersKey.NUM_OF_REGISTERS: 33,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40106,
                    RegistersKey.NUM_OF_REGISTERS: 3,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40121,
                    RegistersKey.NUM_OF_REGISTERS: 70,
                },
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40085,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40100,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.I16,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "DC Power",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["solaredge"],
        },
        {
            ProfileKey.NAME: "solaredge_us",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "SolarEdge US",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "SolarEdge US inverter profile",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40000,
                    RegistersKey.NUM_OF_REGISTERS: 69,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40069,
                    RegistersKey.NUM_OF_REGISTERS: 33,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40106,
                    RegistersKey.NUM_OF_REGISTERS: 3,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40121,
                    RegistersKey.NUM_OF_REGISTERS: 70,
                },
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40085,
                    RegistersKey.NUM_OF_REGISTERS: 1, 
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 0.001,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40100,
                    RegistersKey.NUM_OF_REGISTERS: 1, 
                    RegistersKey.DATA_TYPE: DataTypeKey.I16,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "DC Power",
                    RegistersKey.SCALE_FACTOR: 0.001,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["solaredge"],
        },
        {
            ProfileKey.NAME: "sungrow",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Sungrow",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 4989,
                    RegistersKey.NUM_OF_REGISTERS: 120,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 5112,
                    RegistersKey.NUM_OF_REGISTERS: 50,
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
            ],
            ProfileKey.KEYWORDS: ["sungrow", "Espressif"],
        },
        {
            ProfileKey.NAME: "sungrow_sf",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Sungrow SF",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Sungrow Scale Factor inverter profile",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 4989,
                    RegistersKey.NUM_OF_REGISTERS: 120,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 5112,
                    RegistersKey.NUM_OF_REGISTERS: 50,
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
                    RegistersKey.SCALE_FACTOR: 0.01,
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
            ],
            ProfileKey.KEYWORDS: ["sungrow", "Espressif"],
        },
        {
            ProfileKey.NAME: "sma",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "SMA",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 30000,
                    RegistersKey.NUM_OF_REGISTERS: 10,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 30051,
                    RegistersKey.NUM_OF_REGISTERS: 10,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 30775,
                    RegistersKey.NUM_OF_REGISTERS: 50,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 31085,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 30803,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.U32,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 30775,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.I32,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "DC Power",
                    RegistersKey.SCALE_FACTOR: 1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["sma"],
        },
        {
            ProfileKey.NAME: "fronius",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Fronius Float",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Fronius float inverter profile",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40000,
                    RegistersKey.NUM_OF_REGISTERS: 125,
                }
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40093, # float map v1.0
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.F32,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40107,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.F32,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "DC Power",
                    RegistersKey.SCALE_FACTOR: 1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["fronius", "u-blox ag"],
        },
        {
            ProfileKey.NAME: "fronius_sf",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Fronius SF",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Fronius SF inverter profile",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40000,
                    RegistersKey.NUM_OF_REGISTERS: 125,
                }
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40085, 
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 40100,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.I16,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "DC Power",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["fronius", "u-blox ag"],
        },
        {
            ProfileKey.NAME: "deye",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Deye",
            ProfileKey.PROTOCOL: ProtocolKey.SOLARMAN,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 3,
                    RegistersKey.NUM_OF_REGISTERS: 86,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 514,
                    RegistersKey.NUM_OF_REGISTERS: 125,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 644,
                    RegistersKey.NUM_OF_REGISTERS: 50,
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
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "DC Power",
                    RegistersKey.SCALE_FACTOR: 1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["deye", "high-flying"],
        },
        {
            ProfileKey.NAME: "deye_micro",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Deye Micro-inverter",
            ProfileKey.PROTOCOL: ProtocolKey.SOLARMAN,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 0,
                    RegistersKey.NUM_OF_REGISTERS: 120,
                }
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 79,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 109,
                    RegistersKey.NUM_OF_REGISTERS: 2, # First register is the voltage, second is the current
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "PV 1 Power",
                    RegistersKey.SCALE_FACTOR: 0.1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 111,
                    RegistersKey.NUM_OF_REGISTERS: 2, # First register is the voltage, second is the current
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "PV 2 Power",
                    RegistersKey.SCALE_FACTOR: 0.1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 113,
                    RegistersKey.NUM_OF_REGISTERS: 2, # First register is the voltage, second is the current
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "PV 3 Power",
                    RegistersKey.SCALE_FACTOR: 0.1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["deye", "high-flying"],
        },
        {
            ProfileKey.NAME: "growatt",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Growatt",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 0,
                    RegistersKey.NUM_OF_REGISTERS: 125,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 125,
                    RegistersKey.NUM_OF_REGISTERS: 125,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 1000,
                    RegistersKey.NUM_OF_REGISTERS: 125,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 3000,
                    RegistersKey.NUM_OF_REGISTERS: 125,
                },
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 37,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 3001,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.U32,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "DC Power",
                    RegistersKey.SCALE_FACTOR: 0.1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["growatt", "high-flying"],
        },
        {
            ProfileKey.NAME: "goodwe",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "GoodWe",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 35000,
                    RegistersKey.NUM_OF_REGISTERS: 40,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 35100,
                    RegistersKey.NUM_OF_REGISTERS: 40,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 35141,
                    RegistersKey.NUM_OF_REGISTERS: 40,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 35182,
                    RegistersKey.NUM_OF_REGISTERS: 40,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 36000,
                    RegistersKey.NUM_OF_REGISTERS: 44,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 37000,
                    RegistersKey.NUM_OF_REGISTERS: 23,
                }
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 35123,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 35138,
                    RegistersKey.NUM_OF_REGISTERS: 1, # PV1. First register is the voltage, second is the current
                    RegistersKey.DATA_TYPE: DataTypeKey.I16,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "PV 1 Power",
                    RegistersKey.SCALE_FACTOR: 0.1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["goodwe", "high-flying"],
        },
        {
            ProfileKey.NAME: "ferroamp",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "ferroamp",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 1004,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 1008,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2000,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2016,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2032,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2036,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2040,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2044,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2064,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2068,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2100,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2104,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2108,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2112,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2116,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2120,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2124,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2128,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2132,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2136,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2140,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2144,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 5000,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 5002,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 5004,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 5064,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 5100,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                },
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 2016,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.F32,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 1,
                    RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 5100,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.F32,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "DC Power",
                    RegistersKey.SCALE_FACTOR: 1,
                    RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
                },
            ],
            ProfileKey.KEYWORDS: ["ferroamp"],
        },
        {
            ProfileKey.NAME: "sofar",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Sofar",
            ProfileKey.PROTOCOL: ProtocolKey.SOLARMAN,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1024,
                    RegistersKey.NUM_OF_REGISTERS: 50
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1088,
                    RegistersKey.NUM_OF_REGISTERS: 32
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1152,
                    RegistersKey.NUM_OF_REGISTERS: 48
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1280,
                    RegistersKey.NUM_OF_REGISTERS: 34
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1408,
                    RegistersKey.NUM_OF_REGISTERS: 52,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1472,
                    RegistersKey.NUM_OF_REGISTERS: 4
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1536,
                    RegistersKey.NUM_OF_REGISTERS: 60
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1600,
                    RegistersKey.NUM_OF_REGISTERS: 32
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1664,
                    RegistersKey.NUM_OF_REGISTERS: 28
                },
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1156,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1414,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "PV 1 Power",
                    RegistersKey.SCALE_FACTOR: 0.1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1417,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "PV 2 Power",
                    RegistersKey.SCALE_FACTOR: 0.1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1420,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "PV 3 Power",
                    RegistersKey.SCALE_FACTOR: 0.1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1544,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "%",
                    RegistersKey.DESCRIPTION: "Battery 1 SOC",
                    RegistersKey.SCALE_FACTOR: 1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 1551,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "%",
                    RegistersKey.DESCRIPTION: "Battery 2 SOC",
                    RegistersKey.SCALE_FACTOR: 1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["sofar"],
        },
        {
            ProfileKey.NAME: "solis",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Solis",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Solis inverter profile",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 35000,
                    RegistersKey.NUM_OF_REGISTERS: 1,    # Single U16 register for product definition
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 3000,
                    RegistersKey.NUM_OF_REGISTERS: 125, # 3000-3124
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 3125,
                    RegistersKey.NUM_OF_REGISTERS: 125, # 3125-3249
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 3220,
                    RegistersKey.NUM_OF_REGISTERS: 125, # 3220-3344
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 3281,
                    RegistersKey.NUM_OF_REGISTERS: 125,  # 3281-3405
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 3406,
                    RegistersKey.NUM_OF_REGISTERS: 125,  # 3406-3530
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 3531,
                    RegistersKey.NUM_OF_REGISTERS: 125,  # 3531-3655
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 3656,
                    RegistersKey.NUM_OF_REGISTERS: 125,  # 3656-3780
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 3781,
                    RegistersKey.NUM_OF_REGISTERS: 125,  # 3781-3905
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 33601,
                    RegistersKey.NUM_OF_REGISTERS: 105,  # 33601-33705
                }
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 3043,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 3007,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.U32,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "DC Power",
                    RegistersKey.SCALE_FACTOR: 1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["solis", "Espressif"],
        },
        {
            ProfileKey.NAME: "solis_hybrid",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Solis Hybrid",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Solis inverter profile",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 35000,
                    RegistersKey.NUM_OF_REGISTERS: 1,    # Single U16 register for product definition
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 33000,
                    RegistersKey.NUM_OF_REGISTERS: 125,  # 33000-33124
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 33125,
                    RegistersKey.NUM_OF_REGISTERS: 125,  # 33125-33249
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 33250,
                    RegistersKey.NUM_OF_REGISTERS: 89,   # 33250-33338
                }
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 33094,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
                    RegistersKey.START_REGISTER: 33057,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.U32,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "DC Power",
                    RegistersKey.SCALE_FACTOR: 1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["solis", "Espressif"],
        },
        {
            ProfileKey.NAME: "unknown",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Unknown",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Unknown device profile...",
            ProfileKey.REGISTERS_VERBOSE: [],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 0,
                    RegistersKey.NUM_OF_REGISTERS: 1,
                    RegistersKey.DATA_TYPE: DataTypeKey.U16,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 0.01,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["unknown"],
        },
    ],
    DeviceCategoryKey.METERS: [
        {
            ProfileKey.NAME: "lqt40s",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "LQT40S",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 0,
                    RegistersKey.NUM_OF_REGISTERS: 122,
                }
            ],
            ProfileKey.REGISTERS: [
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 0,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.F32,
                    RegistersKey.UNIT: "Hz",
                    RegistersKey.DESCRIPTION: "Grid frequency",
                    RegistersKey.SCALE_FACTOR: 1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
                {
                    RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
                    RegistersKey.START_REGISTER: 24,
                    RegistersKey.NUM_OF_REGISTERS: 2,
                    RegistersKey.DATA_TYPE: DataTypeKey.F32,
                    RegistersKey.UNIT: "W",
                    RegistersKey.DESCRIPTION: "DC Power",
                    RegistersKey.SCALE_FACTOR: 1,
                    RegistersKey.ENDIANNESS: EndiannessKey.BIG,
                },
            ],
            ProfileKey.KEYWORDS: ["lqt40s"],
        }
    ],
}
