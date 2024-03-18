from ...enums import ProfileKey, RegistersKey, OperationKey, InverterKey

profile = {
    ProfileKey.NAME: InverterKey.SUNGROW.name,
    ProfileKey.DISPLAY_NAME: InverterKey.SUNGROW.value,
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 4989,
            RegistersKey.NUM_OF_REGISTERS: 120
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5112,
            RegistersKey.NUM_OF_REGISTERS: 50
        }
    ]
}
