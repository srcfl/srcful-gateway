from abc import ABC, abstractmethod
from typing import List
from ..profile_keys import ProfileKey, RegistersKey, EndiannessKey, FunctionCodeKey, DataTypeKey
from ..common.types import ModbusDevice
from server.devices.supported_devices.data_models import DERData

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
                 scale_factor_register: int = None):
        self.function_code: FunctionCodeKey = function_code
        self.start_register: int = start_register
        self.offset: int = offset
        self.data_type: DataTypeKey = data_type
        self.unit: str = unit
        self.description: str = description
        self.scale_factor: float = scale_factor
        self.endianness: EndiannessKey = endianness
        self.scale_factor_register: int = scale_factor_register


class ModbusProfile(DeviceProfile):
    """Modbus profile class. Used to define register intervals for Modbus profiles."""

    def __init__(self, profile_data: dict):
        super().__init__(profile_data)
        self.primary_profiles: List[DeviceProfile] = []
        self.sn: RegisterInterval = None
        self.registers_verbose: List[RegisterInterval] = []
        self.registers: List[RegisterInterval] = []

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

    def get_registers_verbose(self) -> List[RegisterInterval]:
        return self.registers_verbose

    def get_registers(self) -> List[RegisterInterval]:
        return self.registers
    
    def dict_to_ders(payload: dict) -> DERData:
        return DERData()

    
