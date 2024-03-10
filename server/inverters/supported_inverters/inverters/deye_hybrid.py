from ...enums import ProfileKey, RegistersKey, OperationKey, InverterKey

profile = {
    ProfileKey.NAME: InverterKey.DEYE_HYBRID.name,
    ProfileKey.DISPLAY_NAME: InverterKey.DEYE_HYBRID.value,
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 3,
            RegistersKey.NUM_OF_REGISTERS: 109
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 150,
            RegistersKey.NUM_OF_REGISTERS: 99
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 250,
            RegistersKey.NUM_OF_REGISTERS: 29
        }
    ]
}