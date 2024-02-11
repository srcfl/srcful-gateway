from ...enums import ProfileKey, RegistersKey, OperationKey

profile = {
    ProfileKey.NAME: "sungrow",
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
        }
    ]
}
