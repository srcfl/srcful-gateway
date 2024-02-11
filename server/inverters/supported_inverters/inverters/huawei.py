from ...enums import ProfileKey, RegistersKey, OperationKey

profile = {
    ProfileKey.NAME: "huawei",
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 30000,
            RegistersKey.NUM_OF_REGISTERS: 35
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32064,
            RegistersKey.NUM_OF_REGISTERS: 31
        }
    ]
}
