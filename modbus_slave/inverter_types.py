SOLAREDGE = "solaredge"
SUNGROW = "sungrow"
HUAWEI = "huawei"
UNKNOWN = "unknown"

READ = "read"
HOLDING = "holding"
SCAN_START = "scan_start"
SCAN_RANGE = "scan_range"

INVERTERS = {
    
    UNKNOWN: {
        READ: [
            {SCAN_START: 30000, SCAN_RANGE: 1}
        ],
    },

    SUNGROW: {
        # https://github.com/bohdan-s/Sungrow-Inverter/raw/main/Modbus%20Information/Communication%20Protocol%20of%20PV%20Grid-Connected%20String%20Inverters_V1.1.37_EN.pdf
        READ: [
            {SCAN_START: 4999, SCAN_RANGE: 110},
            {SCAN_START: 5112, SCAN_RANGE: 50},
        ],
        HOLDING: [
            {SCAN_START: 4999, SCAN_RANGE: 6},
        ],
    },

    SOLAREDGE: {
        # https://knowledge-center.solaredge.com/sites/kc/files/sunspec-implementation-technical-note.pdf
        HOLDING: [
            # Common Model MODBUS Register Mappings
            {SCAN_START: 40000, SCAN_RANGE: 61},

            # Inverter Model MODBUS Register Mappings
            {SCAN_START: 40069, SCAN_RANGE: 37},

            # Multiple MPPT Inverter Extension Model
            {SCAN_START: 40121, SCAN_RANGE: 70},
        ],
    },

    HUAWEI: {
        # https://javierin.com/wp-content/uploads/sites/2/2021/09/Solar-Inverter-Modbus-Interface-Definitions.pdf
        READ: [
            # Model, SN, PN
            {SCAN_START: 30000, SCAN_RANGE: 35},
            # num of strings, mppt trackers...
            {SCAN_START: 30070, SCAN_RANGE: 13},
            # States
            {SCAN_START: 32000, SCAN_RANGE: 1},
            {SCAN_START: 32002, SCAN_RANGE: 3},
            # Alarms
            {SCAN_START: 32008, SCAN_RANGE: 3},
            {SCAN_START: 32016, SCAN_RANGE: 8},
            {SCAN_START: 32064, SCAN_RANGE: 31},
            {SCAN_START: 32106, SCAN_RANGE: 2},
            {SCAN_START: 32114, SCAN_RANGE: 2},
            {SCAN_START: 35300, SCAN_RANGE: 8},
            {SCAN_START: 37113, SCAN_RANGE: 2},
            {SCAN_START: 37200, SCAN_RANGE: 3},
        ],
        HOLDING: [
            {SCAN_START: 40000, SCAN_RANGE: 2},
            {SCAN_START: 40037, SCAN_RANGE: 2},
            {SCAN_START: 40120, SCAN_RANGE: 1},
            {SCAN_START: 40122, SCAN_RANGE: 2},
            {SCAN_START: 40125, SCAN_RANGE: 3},
            {SCAN_START: 40129, SCAN_RANGE: 2},
            {SCAN_START: 40134, SCAN_RANGE: 64},
            {SCAN_START: 40198, SCAN_RANGE: 1},
            {SCAN_START: 40198, SCAN_RANGE: 1},
            # Startup
            {SCAN_START: 40200, SCAN_RANGE: 1},
            # Shutdown
            {SCAN_START: 40201, SCAN_RANGE: 1},
        ],
    }
}
