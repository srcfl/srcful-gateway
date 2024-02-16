from ...enums import ProfileKey, RegistersKey, OperationKey, InverterKey

profile = {
    ProfileKey.NAME: InverterKey.GROWATT.name,
    ProfileKey.DISPLAY_NAME: InverterKey.GROWATT.value,
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 0,
            RegistersKey.NUM_OF_REGISTERS: 92
        }
    ]
}
