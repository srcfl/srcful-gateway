from ...enums import ProfileKey, RegistersKey, OperationKey

profile = {
    ProfileKey.NAME: "solaredge",
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 40000,
            RegistersKey.NUM_OF_REGISTERS: 61
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 40069,
            RegistersKey.NUM_OF_REGISTERS: 37
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 40121,
            RegistersKey.NUM_OF_REGISTERS: 70
        }
    ]
}
