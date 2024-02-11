from ...enums import ProfileKey, RegistersKey, OperationKey

profile = {
    ProfileKey.NAME: "lqt40s",
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 0,
            RegistersKey.NUM_OF_REGISTERS: 2
        }
    ]
}
