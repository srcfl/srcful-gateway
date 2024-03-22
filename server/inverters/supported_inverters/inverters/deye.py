from ...enums import ProfileKey, RegistersKey, OperationKey, InverterKey, ProtocolKey

profile = {
    ProfileKey.NAME: InverterKey.DEYE.name,
    ProfileKey.DISPLAY_NAME: InverterKey.DEYE.value,
    ProfileKey.PROTOCOL: ProtocolKey.SOLARMAN_V5.value,
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 3,
            RegistersKey.NUM_OF_REGISTERS: 86
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 514,
            RegistersKey.NUM_OF_REGISTERS: 55
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 586,
            RegistersKey.NUM_OF_REGISTERS: 5
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 598,
            RegistersKey.NUM_OF_REGISTERS: 38
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 644,
            RegistersKey.NUM_OF_REGISTERS: 9
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 672,
            RegistersKey.NUM_OF_REGISTERS: 7
        },
    ]
}


