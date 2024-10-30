import typing
from ..profile_keys import ProfileKey, RegistersKey, DeviceCategory, ProtocolKey
from .supported_devices import supported_devices
from abc import ABC



class DeviceProfile(ABC):
    """Base class for device profiles. All device profiles must inherit from this class."""
    def __init__(self, profile_data: dict):
        self.name: str = profile_data[ProfileKey.NAME]
        self.version: str = profile_data[ProfileKey.VERSION]
        self.verbose_always: bool = profile_data[ProfileKey.VERBOSE_ALWAYS]
        self.display_name: str = profile_data[ProfileKey.DISPLAY_NAME]
        self.protocol: str = profile_data[ProfileKey.PROTOCOL]
        self.description: str = profile_data[ProfileKey.DESCRIPTION]


class RegisterInterval:
    """Register interval class. Used to define register intervals and function codes for Modbus and Solarman V5 profiles."""
    def __init__(self, operation, start_register, offset):
        self.operation = operation
        self.start_register = start_register
        self.offset = offset


class ModbusProfile(DeviceProfile):
    """Modbus profile class. Used to define register intervals for Modbus profiles."""
    def __init__(self, profile_data: dict):
        super().__init__(profile_data)
        self.registers_verbose = []
        self.registers = []
        
        if ProfileKey.REGISTERS_VERBOSE in profile_data:
            for register_interval in profile_data[ProfileKey.REGISTERS_VERBOSE]:
                self.registers_verbose.append(
                    RegisterInterval(
                        register_interval[RegistersKey.FCODE],
                        register_interval[RegistersKey.START_REGISTER],
                        register_interval[RegistersKey.NUM_OF_REGISTERS]
                    )
                )

        if ProfileKey.REGISTERS in profile_data:
            for register_interval in profile_data[ProfileKey.REGISTERS]:
                self.registers.append(
                    RegisterInterval(
                        register_interval[RegistersKey.FCODE],
                        register_interval[RegistersKey.START_REGISTER],
                        register_interval[RegistersKey.NUM_OF_REGISTERS]
                    )
                )
    
    def get_registers_verbose(self) -> typing.List[RegisterInterval]:
        return self.registers_verbose
    
    def get_registers(self) -> typing.List[RegisterInterval]:
        return self.registers


# class SunSpecProfile(DeviceProfile):
#     """SunSpec profile class. Does not contain any register intervals since they are defined in the SunSpec models."""
#     def __init__(self, profile_data: dict):
#         super().__init__(profile_data)
#         # self.model_ids = profile_data.get('model_ids', [])
        

# class RestApiProfile(DeviceProfile):
#     """Rest API profile class. Used to define base URL and endpoints for Rest API profiles."""
#     def __init__(self, profile_data: dict):
#         super().__init__(profile_data)
#         self.base_url = profile_data.get('base_url')
#         self.endpoints = profile_data.get('endpoints', {})
#         self.auth_method = profile_data.get('auth_method')


class DeviceProfiles:
    """Device profiles class. Used to load and manage device profiles."""
    def __init__(self, device_category: DeviceCategory = DeviceCategory.INVERTERS):
        self.profiles: list[DeviceProfile] = []
        self._load_profiles(device_category)

    def _load_profiles(self, device_category: DeviceCategory):
        for device in supported_devices[device_category]:
            profile = self._create_profile(device)
            if profile:
                self.profiles.append(profile)

    def _create_profile(self, profile_data: dict) -> DeviceProfile:
        protocol = profile_data[ProfileKey.PROTOCOL]
        
        if protocol == ProtocolKey.MODBUS:
            return ModbusProfile(profile_data)
        elif protocol == ProtocolKey.SOLARMAN:
            return ModbusProfile(profile_data)
        elif protocol == ProtocolKey.SUNSPEC:
            return SunSpecProfile(profile_data)
        elif protocol == ProtocolKey.REST:
            return RestApiProfile(profile_data)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    def get(self, name: str) -> DeviceProfile:
        for profile in self.profiles:
            if profile.name.lower() == name.lower():
                return profile
        return None

    def get_supported_devices(self) -> typing.List[DeviceProfile]:
        return self.profiles.copy()
