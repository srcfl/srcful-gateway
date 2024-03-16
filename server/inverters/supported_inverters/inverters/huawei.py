from ...enums import ProfileKey, RegistersKey, OperationKey, InverterKey, ProtocolKey

profile = {
    ProfileKey.NAME: InverterKey.HUAWEI.name,
    ProfileKey.DISPLAY_NAME: InverterKey.HUAWEI.value,
    ProfileKey.REGISTERS: [
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 30000,
            RegistersKey.NUM_OF_REGISTERS: 35
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 30070,
            RegistersKey.NUM_OF_REGISTERS: 13
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32000,
            RegistersKey.NUM_OF_REGISTERS: 1
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32002,
            RegistersKey.NUM_OF_REGISTERS: 3
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32008,
            RegistersKey.NUM_OF_REGISTERS: 3
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32016,
            RegistersKey.NUM_OF_REGISTERS: 8
        },       
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32064,
            RegistersKey.NUM_OF_REGISTERS: 31
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32106,
            RegistersKey.NUM_OF_REGISTERS: 2
        },
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32114,
            RegistersKey.NUM_OF_REGISTERS: 2
        }, 
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 35300,
            RegistersKey.NUM_OF_REGISTERS: 8
        }, 
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 37113,
            RegistersKey.NUM_OF_REGISTERS: 2
        }, 
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 37200,
            RegistersKey.NUM_OF_REGISTERS: 3
        }, 
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 40000,
            RegistersKey.NUM_OF_REGISTERS: 2
        }, 
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 40037,
            RegistersKey.NUM_OF_REGISTERS: 2
        }, 
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 40120,
            RegistersKey.NUM_OF_REGISTERS: 1
        }, 
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 40122,
            RegistersKey.NUM_OF_REGISTERS: 2
        }, 
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 40125,
            RegistersKey.NUM_OF_REGISTERS: 3
        }, 
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 40129,
            RegistersKey.NUM_OF_REGISTERS: 2
        }, 
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 40134,
            RegistersKey.NUM_OF_REGISTERS: 64
        }, 
        {
            RegistersKey.OPERATION: OperationKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 40198,
            RegistersKey.NUM_OF_REGISTERS: 1
        }
    ]
}
