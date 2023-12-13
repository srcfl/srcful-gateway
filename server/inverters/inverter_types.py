SOLAREDGE = "solaredge"
SUNGROW = "sungrow"
SUNGROW_HYBRID = "sungrow_hybrid"
HUAWEI = "huawei"
GROWATT = "growatt"
LQT40S = "lqt40s"
UNKNOWN = "unknown"

OPERATION = "operation"
READ_INPUT = 0x04
READ_HOLDING = 0x03

SCAN_START = "scan_start"
SCAN_RANGE = "scan_range"




INVERTERS = {

    UNKNOWN: [
        {OPERATION: READ_INPUT, SCAN_START: 30000, SCAN_RANGE: 1}
    ],

    GROWATT: [
        # https://www.photovoltaicsolar.in/Growatt_Manual/MAX%20Series%20Modbus%20RTU%20Protocol.pdf
        {OPERATION: READ_INPUT, SCAN_START: 0, SCAN_RANGE: 92},
    ],

    SUNGROW: [
        # https://drive.google.com/file/d/1R5o1pF0ZegdE0IDHUzrvMZVvdOITWMYr/view?usp=drive_link
        {OPERATION: READ_INPUT, SCAN_START: 4999, SCAN_RANGE: 110},
        {OPERATION: READ_INPUT, SCAN_START: 5112, SCAN_RANGE: 50},
    ],

    SUNGROW_HYBRID: [
        # https://drive.google.com/file/d/1O-wIc7Avb3Kb4yOXhKSANcS2w58dSo9J/view?usp=drive_link
        {OPERATION: READ_INPUT, SCAN_START: 4999, SCAN_RANGE: 110},
        {OPERATION: READ_INPUT, SCAN_START: 5112, SCAN_RANGE: 50},
        {OPERATION: READ_INPUT, SCAN_START: 5621, SCAN_RANGE: 2},
        {OPERATION: READ_INPUT, SCAN_START: 12999, SCAN_RANGE: 44},
        {OPERATION: READ_INPUT, SCAN_START: 13106, SCAN_RANGE: 2},
        {OPERATION: READ_HOLDING, SCAN_START: 13073, SCAN_RANGE: 2},
        {OPERATION: READ_HOLDING, SCAN_START: 13086, SCAN_RANGE: 2}
    ],

    SOLAREDGE: [
        # https://knowledge-center.solaredge.com/sites/kc/files/sunspec-implementation-technical-note.pdf
        # Common Model MODBUS Register Mappings
        {OPERATION: READ_HOLDING, SCAN_START: 40000, SCAN_RANGE: 61},
        # Inverter Model MODBUS Register Mappings
        {OPERATION: READ_HOLDING, SCAN_START: 40069, SCAN_RANGE: 37},
        # Multiple MPPT Inverter Extension Model
        {OPERATION: READ_HOLDING, SCAN_START: 40121, SCAN_RANGE: 70},
    ],

    HUAWEI: [
        # https://javierin.com/wp-content/uploads/sites/2/2021/09/Solar-Inverter-Modbus-Interface-Definitions.pdf
        {OPERATION: READ_HOLDING, SCAN_START: 30000, SCAN_RANGE: 35},
        {OPERATION: READ_HOLDING, SCAN_START: 32064, SCAN_RANGE: 31}

        # {OPERATION: READ_HOLDING, SCAN_START: 30000, SCAN_RANGE: 35},
        # {OPERATION: READ_HOLDING, SCAN_START: 30070, SCAN_RANGE: 13},
        # {OPERATION: READ_HOLDING, SCAN_START: 32000, SCAN_RANGE: 1},
        # {OPERATION: READ_HOLDING, SCAN_START: 32002, SCAN_RANGE: 3},
        # {OPERATION: READ_HOLDING, SCAN_START: 32008, SCAN_RANGE: 3},
        # {OPERATION: READ_HOLDING, SCAN_START: 32016, SCAN_RANGE: 8},
        # {OPERATION: READ_HOLDING, SCAN_START: 32064, SCAN_RANGE: 31},
        # {OPERATION: READ_HOLDING, SCAN_START: 32106, SCAN_RANGE: 2},
        # {OPERATION: READ_HOLDING, SCAN_START: 32114, SCAN_RANGE: 2},
        # {OPERATION: READ_HOLDING, SCAN_START: 35300, SCAN_RANGE: 8},
        # {OPERATION: READ_HOLDING, SCAN_START: 37113, SCAN_RANGE: 2},
        # {OPERATION: READ_HOLDING, SCAN_START: 37200, SCAN_RANGE: 3},
        # {OPERATION: READ_HOLDING, SCAN_START: 40000, SCAN_RANGE: 2},
        # {OPERATION: READ_HOLDING, SCAN_START: 40037, SCAN_RANGE: 2},
        # {OPERATION: READ_HOLDING, SCAN_START: 40120, SCAN_RANGE: 1},
        # {OPERATION: READ_HOLDING, SCAN_START: 40122, SCAN_RANGE: 2},
        # {OPERATION: READ_HOLDING, SCAN_START: 40125, SCAN_RANGE: 3},
        # {OPERATION: READ_HOLDING, SCAN_START: 40129, SCAN_RANGE: 2},
        # {OPERATION: READ_HOLDING, SCAN_START: 40134, SCAN_RANGE: 64},
        # {OPERATION: READ_HOLDING, SCAN_START: 40198, SCAN_RANGE: 1},
        # {OPERATION: READ_HOLDING, SCAN_START: 40198, SCAN_RANGE: 1},
        # # Startup
        # {OPERATION: READ_HOLDING, SCAN_START: 40200, SCAN_RANGE: 1},
        # # Shutdown
        # {OPERATION: READ_HOLDING, SCAN_START: 40201, SCAN_RANGE: 1},
    ],

    LQT40S: [
        # https://www.tillquist.com/en/power-automation/cos-phi-phase-angle/lqt400-configurable-multi-transducer-with-2-analogue-outputs-1-1-1-1-1
        {OPERATION: READ_INPUT, SCAN_START: 0, SCAN_RANGE: 2},
    ],
}
