SOLAREDGE = "solaredge"
SUNGROW = "sungrow"
HUAWEI = "huawei"

INVERTERS = {

    SUNGROW: {
        # https://github.com/bohdan-s/Sungrow-Inverter/raw/main/Modbus%20Information/Communication%20Protocol%20of%20PV%20Grid-Connected%20String%20Inverters_V1.1.37_EN.pdf
        "read": [
            {"scan_start": 4999, "scan_range": 110},
            {"scan_start": 5112, "scan_range": 50},
        ],
        "holding": [
            {"scan_start": 4999, "scan_range": 6},
        ],
    },

    SOLAREDGE: {
        # https://knowledge-center.solaredge.com/sites/kc/files/sunspec-implementation-technical-note.pdf
        "holding": [
            # Common Model MODBUS Register Mappings
            {"scan_start": 40000, "scan_range": 61},

            # Inverter Model MODBUS Register Mappings
            {"scan_start": 40069, "scan_range": 37},

            # Multiple MPPT Inverter Extension Model
            {"scan_start": 40121, "scan_range": 70},
        ],
    },

    HUAWEI: {
        # https://javierin.com/wp-content/uploads/sites/2/2021/09/Solar-Inverter-Modbus-Interface-Definitions.pdf
        "read": [
            # Model, SN, PN
            {"scan_start": 30000, "scan_range": 35},
            # num of strings, mppt trackers...
            {"scan_start": 30070, "scan_range": 13},
            # States
            {"scan_start": 32000, "scan_range": 1},
            {"scan_start": 32002, "scan_range": 3},
            # Alarms
            {"scan_start": 32008, "scan_range": 3},
            {"scan_start": 32016, "scan_range": 8},
            {"scan_start": 32064, "scan_range": 31},
            {"scan_start": 32106, "scan_range": 2},
            {"scan_start": 32114, "scan_range": 2},
            {"scan_start": 35300, "scan_range": 8},
            {"scan_start": 37113, "scan_range": 2},
            {"scan_start": 37200, "scan_range": 3},
        ],
        "holding": [
            {"scan_start": 40000, "scan_range": 2},
            {"scan_start": 40037, "scan_range": 2},
            {"scan_start": 40120, "scan_range": 1},
            {"scan_start": 40122, "scan_range": 2},
            {"scan_start": 40125, "scan_range": 3},
            {"scan_start": 40129, "scan_range": 2},
            {"scan_start": 40134, "scan_range": 64},
            {"scan_start": 40198, "scan_range": 1},
            {"scan_start": 40198, "scan_range": 1},
            # Startup
            {"scan_start": 40200, "scan_range": 1},
            # Shutdown
            {"scan_start": 40201, "scan_range": 1},
        ],
    }
}
