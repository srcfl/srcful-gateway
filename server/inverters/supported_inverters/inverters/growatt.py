from ...enums import ProfileKey, RegistersKey, OperationKey

profile = {
    ProfileKey.NAME: "growatt",
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 0,
            RegistersKey.NUM_OF_REGISTERS: 92
        }
    ]
}
