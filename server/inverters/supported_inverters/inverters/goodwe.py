from ...enums import ProfileKey, RegistersKey, OperationKey, InverterKey

profile = {
    ProfileKey.NAME: InverterKey.GOODWE.name,
    ProfileKey.DISPLAY_NAME: InverterKey.GOODWE.value,
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 1280,
            RegistersKey.NUM_OF_REGISTERS: 68
        }
    ]
}
