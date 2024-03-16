from ...enums import ProfileKey, RegistersKey, OperationKey, InverterKey, ProtocolKey

profile = {
    ProfileKey.NAME: InverterKey.SUNGROW_HYBRID.name,
    ProfileKey.DISPLAY_NAME: InverterKey.SUNGROW_HYBRID.value,
    ProfileKey.PROTOCOL: ProtocolKey.MODBUS.value,
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 4999,
            RegistersKey.NUM_OF_REGISTERS: 110
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5112,
            RegistersKey.NUM_OF_REGISTERS: 50
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 13000,
            RegistersKey.NUM_OF_REGISTERS: 6
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 13028,
            RegistersKey.NUM_OF_REGISTERS: 6
        }
    ],
    "controlRegister": {
        "enableControl": {
            "address": 30099,
            "type": "uint16",
            "unit": "-",
            "description": "1 or 0 to enable or disable the inverter."
        },
        "activePower": {
            "address": 30100,
            "type": "uint16",
            "unit": "W",
            "description": "Active power output of the inverter."
        }
    }
}
