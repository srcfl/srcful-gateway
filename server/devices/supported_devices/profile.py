from abc import ABC, abstractmethod
from typing import List
from ..profile_keys import ProfileKey, RegistersKey, EndiannessKey, FunctionCodeKey, DataTypeKey
from ..common.types import ModbusDevice
import struct
import logging
from typing import Tuple, Optional, Union
from server.e_system.types import EBaseType

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseProfile(ABC):

    @abstractmethod
    def profile_is_valid(self, device: ModbusDevice) -> bool:
        """
        This method is used to check if the profile is valid.
        It can for example check if it is possible to retrieve the serial number or other values from the device.
        """
        raise NotImplementedError("Subclasses must implement this method")


class DeviceProfile(BaseProfile):
    """Base class for device profiles. All device profiles must inherit from this class."""

    def __init__(self, profile_data: dict):
        self.name: str = profile_data[ProfileKey.NAME]
        self.maker: str = profile_data[ProfileKey.MAKER]
        self.version: str = profile_data[ProfileKey.VERSION]
        self.verbose_always: bool = profile_data[ProfileKey.VERBOSE_ALWAYS]
        self.display_name: str = profile_data[ProfileKey.DISPLAY_NAME]
        self.protocol: str = profile_data[ProfileKey.PROTOCOL]
        self.description: str = profile_data[ProfileKey.DESCRIPTION]
        self.keywords: List[str] = profile_data[ProfileKey.KEYWORDS]
        self.always_include: List[int] = profile_data[ProfileKey.ALWAYS_INCLUDE]


class RegisterInterval:
    """Register interval class. Used to define register intervals and function codes for Modbus and Solarman V5 profiles."""

    def __init__(self,
                 function_code: FunctionCodeKey,
                 start_register: int,
                 offset: int,
                 data_type: DataTypeKey = DataTypeKey.U16,
                 unit: str = "N/A",
                 description: str = "N/A",
                 scale_factor: float = 1.0,
                 endianness: EndiannessKey = EndiannessKey.BIG,
                 scale_factor_register: int = None,
                 raw_registers: List[int] = None,
                 decoded_value: float = None):
        self.function_code: FunctionCodeKey = function_code
        self.start_register: int = start_register
        self.offset: int = offset
        self.data_type: DataTypeKey = data_type
        self.unit: str = unit
        self.description: str = description
        self.scale_factor: float = scale_factor
        self.endianness: EndiannessKey = endianness
        self.scale_factor_register: int = scale_factor_register
        self.raw_registers: List[int] = raw_registers
        self.decoded_value: float = decoded_value

    def decode_value(self) -> Tuple[bytearray, Optional[Union[int, float, str]]]:

        if self.raw_registers is None:
            return None, None

        raw = bytearray()

        for register in self.raw_registers:
            raw.extend(register.to_bytes(2, "big"))

        # logger.debug(f"Interpreting value - DataType: {self.data_type}, Raw: {raw.hex()}, ScaleFactor: {self.scale_factor}")

        try:
            # Handle register pair endianness (if applicable)
            # Example for a 32-bit value (2 registers, 4 bytes total):
            # Original bytes: [0x12][0x34][0x56][0x78]
            # Register 1: [0x12][0x34]
            # Register 2: [0x56][0x78]
            #
            # Big Endian (default): [R1][R2] = [0x12][0x34][0x56][0x78] = 0x12345678
            # Little Endian:        [R2][R1] = [0x56][0x78][0x12][0x34] = 0x56781234
            #
            # Note: Bytes within each register stay in big-endian order
            # as per Modbus specification. We only swap the register order,
            # not the bytes within registers.

            # For multi-register values, we need to:
            # 1. Keep the raw bytes as they are for big-endian
            # 2. For little-endian, interpret the value by swapping register order
            value_bytes = raw
            if len(raw) > 2 and self.endianness == EndiannessKey.LITTLE:
                # For little-endian, we'll read the bytes in reverse register order
                # but keep bytes within each register in their original order
                registers = [raw[i:i+2] for i in range(0, len(raw), 2)]
                value_bytes = bytearray().join(registers[::-1])
            else:
                value_bytes = raw

            if self.data_type == DataTypeKey.U16:
                value = int.from_bytes(value_bytes[0:2], "big", signed=False)
                self.decoded_value = value * self.scale_factor
                return value_bytes, self.decoded_value

            elif self.data_type == DataTypeKey.I16:
                value = int.from_bytes(value_bytes[0:2], "big", signed=True)
                self.decoded_value = value * self.scale_factor
                return value_bytes, self.decoded_value

            elif self.data_type == DataTypeKey.U32:
                value = int.from_bytes(value_bytes[0:4], "big", signed=False)
                self.decoded_value = value * self.scale_factor
                return value_bytes, self.decoded_value

            elif self.data_type == DataTypeKey.I32:
                value = int.from_bytes(value_bytes[0:4], "big", signed=True)
                self.decoded_value = value * self.scale_factor
                return value_bytes, self.decoded_value

            elif self.data_type == DataTypeKey.F32:
                value = struct.unpack(">f", value_bytes[0:4])[0]
                self.decoded_value = value * self.scale_factor
                return value_bytes, self.decoded_value

            elif self.data_type == DataTypeKey.U64:
                value = int.from_bytes(value_bytes[0:8], "big", signed=False)
                self.decoded_value = value * self.scale_factor
                return value_bytes, self.decoded_value

            elif self.data_type == DataTypeKey.I64:
                value = int.from_bytes(value_bytes[0:8], "big", signed=True)
                self.decoded_value = value * self.scale_factor
                return value_bytes, self.decoded_value

            elif self.data_type == DataTypeKey.STR:
                # For strings, we just decode the bytes as they are
                # Register order swapping (if any) is already handled above
                self.decoded_value = value_bytes.decode("ascii").rstrip('\x00')
                return value_bytes, self.decoded_value

            return raw, None

        except Exception as e:
            logger.error(f"Error interpreting value: {str(e)}")
            return raw, None


class ModbusProfile(DeviceProfile):
    """Modbus profile class. Used to define register intervals for Modbus profiles."""

    def __init__(self, profile_data: dict):
        super().__init__(profile_data)
        self.primary_profiles: List[DeviceProfile] = []
        self.sn: RegisterInterval = None
        self.registers_verbose: List[RegisterInterval] = []
        self.registers: List[RegisterInterval] = []
        self.all_registers: List[RegisterInterval] = []

        if ProfileKey.SN in profile_data:
            sn_reg = profile_data[ProfileKey.SN]

            self.sn = RegisterInterval(
                sn_reg[RegistersKey.FUNCTION_CODE],
                sn_reg[RegistersKey.START_REGISTER],
                sn_reg[RegistersKey.NUM_OF_REGISTERS],
                sn_reg[RegistersKey.DATA_TYPE],
                sn_reg[RegistersKey.UNIT],
                sn_reg[RegistersKey.DESCRIPTION],
                sn_reg[RegistersKey.SCALE_FACTOR],
                sn_reg[RegistersKey.ENDIANNESS]
            )

        if ProfileKey.REGISTERS_VERBOSE in profile_data:
            for register_interval in profile_data[ProfileKey.REGISTERS_VERBOSE]:
                self.registers_verbose.append(
                    RegisterInterval(
                        register_interval[RegistersKey.FUNCTION_CODE],
                        register_interval[RegistersKey.START_REGISTER],
                        register_interval[RegistersKey.NUM_OF_REGISTERS],
                    )
                )

        if ProfileKey.REGISTERS in profile_data:
            for register_interval in profile_data[ProfileKey.REGISTERS]:
                self.registers.append(
                    RegisterInterval(
                        register_interval[RegistersKey.FUNCTION_CODE],
                        register_interval[RegistersKey.START_REGISTER],
                        register_interval[RegistersKey.NUM_OF_REGISTERS],
                        register_interval[RegistersKey.DATA_TYPE],
                        register_interval[RegistersKey.UNIT],
                        register_interval[RegistersKey.DESCRIPTION],
                        register_interval[RegistersKey.SCALE_FACTOR],
                        register_interval[RegistersKey.ENDIANNESS],
                        register_interval.get(RegistersKey.SCALE_FACTOR_REGISTER, None)
                    )
                )

        if ProfileKey.ALL_REGISTERS in profile_data:
            for register_interval in profile_data[ProfileKey.ALL_REGISTERS]:
                self.all_registers.append(
                    RegisterInterval(
                        register_interval[RegistersKey.FUNCTION_CODE],
                        register_interval[RegistersKey.START_REGISTER],
                        register_interval[RegistersKey.NUM_OF_REGISTERS],
                        register_interval[RegistersKey.DATA_TYPE],
                        register_interval[RegistersKey.UNIT],
                        register_interval[RegistersKey.DESCRIPTION],
                        register_interval[RegistersKey.SCALE_FACTOR],
                        register_interval[RegistersKey.ENDIANNESS]
                    )
                )

    def get_registers_verbose(self) -> List[RegisterInterval]:
        return self.registers_verbose

    def get_registers(self) -> List[RegisterInterval]:
        return self.registers

    def get_register(self, register: int) -> Optional[RegisterInterval]:
        for reg in self.all_registers:
            if reg.start_register == register:
                return reg
        return None

    def get_register_interval(self, register: int, register_intervals: List[RegisterInterval]) -> RegisterInterval:
        for register_interval in register_intervals:
            if register_interval.start_register == register:
                return register_interval
        return None

    def get_decoded_registers(self, harvest_data: dict) -> List[RegisterInterval]:

        decoded_registers: List[RegisterInterval] = []

        for register in harvest_data.keys():
            # logger.debug(f"Decoding register: {register}")
            # logger.debug(f"Harvest data: {harvest_data}")
            # logger.debug(f"Register interval: {self.get_register(register)}")
            reg_interval: RegisterInterval = self.get_register(register)
            if reg_interval is not None:
                reg_interval.raw_registers = [harvest_data[int(register) + i] for i in range(reg_interval.offset)]
                reg_interval.decode_value()
                decoded_registers.append(reg_interval)

        return decoded_registers

    def _get_esystem_data(self, device_sn: str, timestamp_ms: int, harvest: dict) -> List[EBaseType]:
        return []
