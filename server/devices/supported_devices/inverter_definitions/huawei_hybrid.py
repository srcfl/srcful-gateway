from ...profile_keys import (
    ProtocolKey,
    ProfileKey,
    RegistersKey,
    FunctionCodeKey,
    DataTypeKey,
    EndiannessKey,
)
from ..profile import ModbusProfile
from ...common.types import ModbusDevice
from ...registerValue import RegisterValue
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class HuaweiHybridProfile(ModbusProfile):
    def __init__(self):
        super().__init__(huawei_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return self._battery_has_voltage(device)

    def _battery_has_voltage(self, device: ModbusDevice) -> bool:
        battery_voltage = RegisterValue(address=37763,
                                        size=2,
                                        function_code=FunctionCodeKey.READ_HOLDING_REGISTERS,
                                        data_type=DataTypeKey.U16,
                                        scale_factor=0.1,
                                        endianness=EndiannessKey.BIG)

        _, _, value = battery_voltage.read_value(device)

        logger.info(f"Battery voltage: {value}V")

        return value != None and value > 0


huawei_profile = {
    ProfileKey.NAME: "huawei_hybrid",
    ProfileKey.MAKER: "Huawei",
    ProfileKey.VERSION: "V1.1b3",
    ProfileKey.VERBOSE_ALWAYS: False,
    ProfileKey.DISPLAY_NAME: "Huawei Hybrid",
    ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
    ProfileKey.DESCRIPTION: "Huawei Hybrid inverter profile...",
    ProfileKey.SN: {
        RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
        RegistersKey.START_REGISTER: 30015,
        RegistersKey.NUM_OF_REGISTERS: 10,
        RegistersKey.DATA_TYPE: DataTypeKey.STR,
        RegistersKey.UNIT: "",
        RegistersKey.DESCRIPTION: "Serial number",
        RegistersKey.SCALE_FACTOR: 1,
        RegistersKey.ENDIANNESS: EndiannessKey.BIG,
    },
    ProfileKey.ALWAYS_INCLUDE: [],
    ProfileKey.REGISTERS_VERBOSE: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 30000,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32000,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 37000,
            RegistersKey.NUM_OF_REGISTERS: 69,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 37700,
            RegistersKey.NUM_OF_REGISTERS: 100,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47000,
            RegistersKey.NUM_OF_REGISTERS: 1,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47028,
            RegistersKey.NUM_OF_REGISTERS: 62,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47100,
            RegistersKey.NUM_OF_REGISTERS: 10,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47242,
            RegistersKey.NUM_OF_REGISTERS: 9,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47299,
            RegistersKey.NUM_OF_REGISTERS: 1,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47415,
            RegistersKey.NUM_OF_REGISTERS: 20,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47590,
            RegistersKey.NUM_OF_REGISTERS: 2,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47604,
            RegistersKey.NUM_OF_REGISTERS: 2,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47750,
            RegistersKey.NUM_OF_REGISTERS: 6,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 37100,
            RegistersKey.NUM_OF_REGISTERS: 39,
        }
    ],
    ProfileKey.REGISTERS: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32085,
            RegistersKey.NUM_OF_REGISTERS: 1,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "Hz",
            RegistersKey.DESCRIPTION: "Grid frequency",
            RegistersKey.SCALE_FACTOR: 0.01,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32064,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.I32,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "DC Power",
            RegistersKey.SCALE_FACTOR: 0.001,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
    ],
    ProfileKey.KEYWORDS: ["huawei", "sun2000"],
}
