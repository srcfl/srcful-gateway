from ..profile_keys import ProtocolKey, ProfileKey, RegistersKey, OperationKey, DeviceCategory

supported_devices = {
    DeviceCategory.INVERTERS: [
        {
            # Enphase REST API profile
            ProfileKey.NAME: "enphase",
            ProfileKey.VERSION: "V0.1",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Enphase",
            ProfileKey.PROTOCOL: ProtocolKey.REST_API,
            ProfileKey.DESCRIPTION: "Enphase Envoy REST API",
            ProfileKey.BASE_URL: 'http://envoy.local/',
            ProfileKey.ENDPOINTS: {
                'meters': 'ivp/meters',
                'readings': 'ivp/meters/readings',
                'energy': 'ivp/pdm/energy',
                'inverters': 'api/v1/production/inverters'
            }
        },
        {
            # SunSpec profile
            ProfileKey.NAME: "sunspec_inverter",
            ProfileKey.VERSION: "V1.0",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "SunSpec Inverter",
            ProfileKey.PROTOCOL: ProtocolKey.SUNSPEC,
            ProfileKey.DESCRIPTION: "SunSpec-compatible inverter",
        },
        {
            ProfileKey.NAME: "huawei",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Huawei",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 30000, RegistersKey.NUM_OF_REGISTERS: 125},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 32000, RegistersKey.NUM_OF_REGISTERS: 125}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 32085, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 32064, RegistersKey.NUM_OF_REGISTERS: 2}
            ]
        },
        {
            ProfileKey.NAME: "solaredge",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "SolarEdge",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 40000, RegistersKey.NUM_OF_REGISTERS: 69},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 40069, RegistersKey.NUM_OF_REGISTERS: 33},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 40106, RegistersKey.NUM_OF_REGISTERS: 3},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 40121, RegistersKey.NUM_OF_REGISTERS: 70}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 40085, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 40100, RegistersKey.NUM_OF_REGISTERS: 2}
            ]
        },
        {
            ProfileKey.NAME: "sungrow",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Sungrow",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 4989, RegistersKey.NUM_OF_REGISTERS: 120},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 5112, RegistersKey.NUM_OF_REGISTERS: 50}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 5035, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 5016, RegistersKey.NUM_OF_REGISTERS: 2}
            ]
        },
        {
            ProfileKey.NAME: "sungrow_hybrid",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Sungrow Hybrid",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 4989, RegistersKey.NUM_OF_REGISTERS: 120},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 5112, RegistersKey.NUM_OF_REGISTERS: 50},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 13000, RegistersKey.NUM_OF_REGISTERS: 50}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 5035, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 5016, RegistersKey.NUM_OF_REGISTERS: 2}
            ]
        },
        {
            ProfileKey.NAME: "sma",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "SMA",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 30000, RegistersKey.NUM_OF_REGISTERS: 10},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 30051, RegistersKey.NUM_OF_REGISTERS: 10},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 30775, RegistersKey.NUM_OF_REGISTERS: 50},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 31085, RegistersKey.NUM_OF_REGISTERS: 2}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 30803, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 30775, RegistersKey.NUM_OF_REGISTERS: 2}
            ]
        },
        {
            ProfileKey.NAME: "fronius",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Fronius",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Fronius inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 40000, RegistersKey.NUM_OF_REGISTERS: 125}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 40093, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 40107, RegistersKey.NUM_OF_REGISTERS: 2}
            ]
        },
        {
            ProfileKey.NAME: "fronius_sunspec",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Fronius (SunSpec)",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Fronius inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 40000, RegistersKey.NUM_OF_REGISTERS: 125}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 40085, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 40100, RegistersKey.NUM_OF_REGISTERS: 2}
            ]
        },
        {
            ProfileKey.NAME: "deye",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Deye",
            ProfileKey.PROTOCOL: ProtocolKey.SOLARMAN_V5,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 3, RegistersKey.NUM_OF_REGISTERS: 86},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 514, RegistersKey.NUM_OF_REGISTERS: 125},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 644, RegistersKey.NUM_OF_REGISTERS: 50}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 609, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 672, RegistersKey.NUM_OF_REGISTERS: 2}
            ]
        },
        {
            ProfileKey.NAME: "deye_hybrid",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Deye Hybrid",
            ProfileKey.PROTOCOL: ProtocolKey.SOLARMAN_V5,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 3, RegistersKey.NUM_OF_REGISTERS: 86},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 514, RegistersKey.NUM_OF_REGISTERS: 125},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 644, RegistersKey.NUM_OF_REGISTERS: 50}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 609, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 672, RegistersKey.NUM_OF_REGISTERS: 2}
            ]
        },
        {
            ProfileKey.NAME: "growatt",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "Growatt",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 0, RegistersKey.NUM_OF_REGISTERS: 92}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 37, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 1, RegistersKey.NUM_OF_REGISTERS: 3}
            ]
        },
        {
            ProfileKey.NAME: "goodwe",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "GoodWe",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 1280, RegistersKey.NUM_OF_REGISTERS: 68}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 1304, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 1323, RegistersKey.NUM_OF_REGISTERS: 1}
            ]
        },
        {
            ProfileKey.NAME: "ferroamp",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "ferroamp",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 1004, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 1008, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2000, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2016, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2032, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2036, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2040, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2044, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2064, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2068, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2100, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2104, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2108, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2112, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2116, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2120, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2124, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2128, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2132, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2136, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2140, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2144, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 5000, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 5002, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 5004, RegistersKey.NUM_OF_REGISTERS: 1},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 5064, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 5100, RegistersKey.NUM_OF_REGISTERS: 2}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 2016, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_INPUT_REGISTERS, RegistersKey.START_REGISTER: 5100, RegistersKey.NUM_OF_REGISTERS: 2}
            ]
        }
    ],
    DeviceCategory.METERS: [
        {
            ProfileKey.NAME: "lqt40s",
            ProfileKey.VERSION: "V1.1b3",
            ProfileKey.VERBOSE_ALWAYS: False,
            ProfileKey.DISPLAY_NAME: "LQT40S",
            ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
            ProfileKey.DESCRIPTION: "Another inverter profile...",
            ProfileKey.REGISTERS_VERBOSE: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 0, RegistersKey.NUM_OF_REGISTERS: 2}
            ],
            ProfileKey.REGISTERS: [
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 0, RegistersKey.NUM_OF_REGISTERS: 2},
                {RegistersKey.FCODE: OperationKey.READ_HOLDING_REGISTERS, RegistersKey.START_REGISTER: 0, RegistersKey.NUM_OF_REGISTERS: 2}
            ]
        }
    ]
}