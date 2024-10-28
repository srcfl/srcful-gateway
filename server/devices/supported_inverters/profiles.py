# To add a new inverter, create a new file in the inverters folder and import it here
# Then add the new inverter to the inverters list and it will be supported by the gateway (PoS)
import typing
from ..enums import ProfileKey, RegistersKey, OperationKey, DeviceCategory
import json
from .supported_devices import supported_devices

inverters = []

for device in supported_devices[DeviceCategory.INVERTERS]:
    inverters.append(device)

class RegisterInterval:
    def __init__(self, operation, start_register, offset):
        self.operation = operation
        self.start_register = start_register
        self.offset = offset


class InverterProfile:
    def __init__(self, inverter_profile):
        self.name: str = inverter_profile[ProfileKey.NAME]
        self.version: str = inverter_profile[ProfileKey.VERSION]
        self.verbose_always: bool = inverter_profile[ProfileKey.VERBOSE_ALWAYS]
        self.display_name: str = inverter_profile[ProfileKey.DISPLAY_NAME]
        self.protocol: str = inverter_profile[ProfileKey.PROTOCOL]
        self.description: str = inverter_profile[ProfileKey.DESCRIPTION]

        self.registers_verbose = []
        self.registers = []

        for register_interval in inverter_profile[ProfileKey.REGISTERS_VERBOSE]:
            self.registers_verbose.append(
                RegisterInterval(
                    register_interval[RegistersKey.FCODE],
                    register_interval[RegistersKey.START_REGISTER],
                    register_interval[RegistersKey.NUM_OF_REGISTERS]
                )
            )

        for register_interval in inverter_profile[ProfileKey.REGISTERS]:
            self.registers.append(
                RegisterInterval(register_interval[RegistersKey.FCODE],
                                 register_interval[RegistersKey.START_REGISTER],
                                 register_interval[RegistersKey.NUM_OF_REGISTERS])
            )

    def get_registers_verbose(self) -> typing.List[RegisterInterval]:
        return self.registers_verbose
    
    def get_registers(self) -> typing.List[RegisterInterval]:
        return self.registers



class InverterProfiles:
    def __init__(self):
        self.profiles: list[InverterProfile] = []

        for inverter in inverters:
            self.profiles.append(InverterProfile(inverter))

    def get(self, name: str) -> InverterProfile:
        for profile in self.profiles:
            if profile.name.lower() == name.lower():
                return profile
        return None

    def get_supported_inverters(self) -> typing.List[InverterProfile]:
        return [profile for profile in self.profiles]
