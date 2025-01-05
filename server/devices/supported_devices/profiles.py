import typing
from ..profile_keys import ProfileKey, RegistersKey, DeviceCategoryKey, ProtocolKey, EndiannessKey, FunctionCodeKey
from ..profile_keys import DataTypeKey
from .supported_devices import supported_devices
from abc import ABC
from typing import List


class DeviceProfile(ABC):
    """Base class for device profiles. All device profiles must inherit from this class."""
    def __init__(self, profile_data: dict):
        self.name: str = profile_data[ProfileKey.NAME]
        self.version: str = profile_data[ProfileKey.VERSION]
        self.verbose_always: bool = profile_data[ProfileKey.VERBOSE_ALWAYS]
        self.display_name: str = profile_data[ProfileKey.DISPLAY_NAME]
        self.protocol: str = profile_data[ProfileKey.PROTOCOL]
        self.description: str = profile_data[ProfileKey.DESCRIPTION]
        self.keywords: List[str] = profile_data[ProfileKey.KEYWORDS]


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
                 endianness: EndiannessKey = EndiannessKey.BIG):
        self.function_code: FunctionCodeKey = function_code
        self.start_register: int = start_register
        self.offset: int = offset
        self.data_type: DataTypeKey = data_type
        self.unit: str = unit
        self.description: str = description
        self.scale_factor: float = scale_factor
        self.endianness: EndiannessKey = endianness


class ModbusProfile(DeviceProfile):
    """Modbus profile class. Used to define register intervals for Modbus profiles."""
    def __init__(self, profile_data: dict):
        super().__init__(profile_data)
        self.registers_verbose: List[RegisterInterval] = []
        self.registers: List[RegisterInterval] = []
        
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
                        register_interval[RegistersKey.ENDIANNESS]
                    )
                )
    
    def get_registers_verbose(self) -> typing.List[RegisterInterval]:
        return self.registers_verbose
    
    def get_registers(self) -> typing.List[RegisterInterval]:
        return self.registers
    

class ModbusDeviceProfiles:
    """Device profiles class. Used to load and manage device profiles."""
    def __init__(self, device_category: DeviceCategoryKey = DeviceCategoryKey.INVERTERS):
        self.profiles: list[DeviceProfile] = []
        self._load_profiles(device_category)

    def _load_profiles(self, device_category: DeviceCategoryKey):
        for device in supported_devices[device_category]:
            profile = self._create_profile(device)
            if profile:
                self.profiles.append(profile)

    def _create_profile(self, profile_data: dict) -> DeviceProfile:
        protocol = profile_data[ProfileKey.PROTOCOL]
        
        if protocol == ProtocolKey.MODBUS or protocol == ProtocolKey.SOLARMAN:
            return ModbusProfile(profile_data)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    def get(self, name: str) -> DeviceProfile | None:
        for profile in self.profiles:
            if profile.name.lower() == name.lower():
                return profile
        return None

    def get_supported_devices(self) -> typing.List[DeviceProfile]:
        return self.profiles.copy()
