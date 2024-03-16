from ...enums import ProfileKey, RegistersKey, OperationKey, InverterKey, ProtocolKey

profile = {
    ProfileKey.NAME: InverterKey.LQT40S.name,
    ProfileKey.DISPLAY_NAME: InverterKey.LQT40S.value,
    ProfileKey.PROTOCOL: ProtocolKey.MODBUS.value,
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 0,
            RegistersKey.NUM_OF_REGISTERS: 2
        }
    ]
}
