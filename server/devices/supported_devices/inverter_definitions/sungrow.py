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


class SungrowProfile(ModbusProfile):
    def __init__(self):
        super().__init__(sungrow_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return True
    
    def is_controllable(self) -> bool:
        return True

    def init_device(self, device: ModbusDevice) -> bool:
        reg = 13049  # Grid Mode
        val = 2  # Forced mode
        success = RegisterValue.write_single(device=device, address=reg, value=val)
        if success:
            logger.info(f"Successfully set register {reg} to {val}")

        reg = 13050  # Charging/Discharging mode
        val = 204  # Stop
        success = success and RegisterValue.write_single(device=device, address=reg, value=val)
        if success:
            logger.info(f"Successfully set register {reg} to {val}")

        reg = 33046  # Max charge power
        val = 500
        success = success and RegisterValue.write_single(device=device, address=reg, value=val)
        if success:
            logger.info(f"Successfully set register {reg} to {val}")

        reg = 33047  # Max discharge power
        val = 500
        success = success and RegisterValue.write_single(device=device, address=reg, value=val)
        if success:
            logger.info(f"Successfully set register {reg} to {val}")

        return success

    def deinit_device(self, device: ModbusDevice) -> bool:
        reg = 13050  # Charging/Discharging mode
        val = 204  # Stop
        success = RegisterValue.write_single(device=device, address=reg, value=val)
        if success:
            logger.info(f"Successfully set register {reg} to {val}")

        reg = 13049  # Grid Mode
        val = 0  # self-consumption mode
        success = success and RegisterValue.write_single(device=device, address=reg, value=val)
        if success:
            logger.info(f"Successfully set register {reg} to {val}")

        return success
    
    def set_battery_power(self, device: ModbusDevice, power: int) -> bool:
        success = RegisterValue.write_single(device=device, address=13051, value=abs(power))
        if success:
            logger.info(f"Successfully set register 13050 to {abs(power)}")
        
        command = 170 if power > 0 else 187 if power < 0 else 204 #"0xAA(170):Charge; 0xBB(187):Discharge; 0xCC(204):Stop",
        success = success and RegisterValue.write_single(device=device, address=13050, value=command)
        if success:
            logger.info(f"Successfully set register 13050 to {command}")

        return success


sungrow_profile = {
    ProfileKey.NAME: "sungrow",
    ProfileKey.MAKER: "Sungrow",
    ProfileKey.VERSION: "V1.1b3",
    ProfileKey.VERBOSE_ALWAYS: False,
    ProfileKey.DISPLAY_NAME: "Sungrow",
    ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
    ProfileKey.DESCRIPTION: "Another inverter profile...",
    ProfileKey.SN: {
        RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
        RegistersKey.START_REGISTER: 4989,
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
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 4949,
            RegistersKey.NUM_OF_REGISTERS: 87,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5213,
            RegistersKey.NUM_OF_REGISTERS: 28,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5602,
            RegistersKey.NUM_OF_REGISTERS: 36,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6099,
            RegistersKey.NUM_OF_REGISTERS: 96,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6195,
            RegistersKey.NUM_OF_REGISTERS: 94,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6289,
            RegistersKey.NUM_OF_REGISTERS: 96,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6385,
            RegistersKey.NUM_OF_REGISTERS: 83,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6468,
            RegistersKey.NUM_OF_REGISTERS: 96,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6564,
            RegistersKey.NUM_OF_REGISTERS: 83,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6647,
            RegistersKey.NUM_OF_REGISTERS: 96,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6743,
            RegistersKey.NUM_OF_REGISTERS: 83,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 12999,
            RegistersKey.NUM_OF_REGISTERS: 119,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 13049,
            RegistersKey.NUM_OF_REGISTERS: 51,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 33041,
            RegistersKey.NUM_OF_REGISTERS: 7,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 33147,
            RegistersKey.NUM_OF_REGISTERS: 1,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 31221,
            RegistersKey.NUM_OF_REGISTERS: 1,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 33207,
            RegistersKey.NUM_OF_REGISTERS: 2,
        },
    ],
    ProfileKey.REGISTERS: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5035,
            RegistersKey.NUM_OF_REGISTERS: 1,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "Hz",
            RegistersKey.DESCRIPTION: "Grid frequency",
            RegistersKey.SCALE_FACTOR: 0.1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5016,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.U32,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "DC Power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
        {
            RegistersKey.NAME: "Total Active Power",
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 13009,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.I32,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "Total active power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
        },
        {
            RegistersKey.NAME: "Battery Power",
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 13021,
            RegistersKey.NUM_OF_REGISTERS: 1,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "Battery power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
        {
            RegistersKey.NAME: "Running State",
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 13000,
            RegistersKey.NUM_OF_REGISTERS: 1,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "",
            RegistersKey.DESCRIPTION: "Current running state of the inverter, refer to Appendix 1.2",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
    ],
    ProfileKey.KEYWORDS: ["sungrow", "Espressif"],
}
