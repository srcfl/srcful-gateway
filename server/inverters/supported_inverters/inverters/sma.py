from ...enums import ProfileKey, RegistersKey, OperationKey, InverterKey, ProtocolKey

profile = {
    ProfileKey.NAME: InverterKey.SMA.name,
    ProfileKey.DISPLAY_NAME: InverterKey.SMA.value,
    ProfileKey.PROTOCOL: ProtocolKey.MODBUS.value,
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 30000,
            RegistersKey.NUM_OF_REGISTERS: 60
        },       
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 30775,
            RegistersKey.NUM_OF_REGISTERS: 125
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 31085,
            RegistersKey.NUM_OF_REGISTERS: 2
        }
    ]
}
