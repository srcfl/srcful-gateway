# To add a new inverter, create a new file in the inverters folder and import it here
# Then add the new inverter to the inverters list and it will be supported by the gateway (PoS)
import typing
from ..enums import ProfileKey, RegistersKey, OperationKey
import json

inverters = []

# Load all inverters
with open("server/inverters/supported_inverters/inverters/inverters.json") as f:
    data = json.load(f)
    for d in data["inverters"]:
        inverters.append(d)


class RegisterInterval:
    def __init__(self, operation, start_register, offset):
        self.operation = operation
        self.start_register = start_register
        self.offset = offset


class InverterProfile:
    def __init__(self, inverter_profile):
        inverter_profile = json.loads(json.dumps(inverter_profile))

        self.name: str = inverter_profile[ProfileKey.NAME.value]
        self.version: str = inverter_profile[ProfileKey.VERSION.value]
        self.verbose_always: bool = inverter_profile[ProfileKey.VERBOSE_ALWAYS.value]
        self.model_group: str = inverter_profile[ProfileKey.MODEL_GROUP.value]
        self.display_name: str = inverter_profile[ProfileKey.DISPLAY_NAME.value]
        self.protocol: str = inverter_profile[ProfileKey.PROTOCOL.value]
        self.description: str = inverter_profile[ProfileKey.DESCRIPTION.value]

        self.registers_verbose = []
        self.registers = []

        for register_interval in inverter_profile[ProfileKey.REGISTERS_VERBOSE.value]:
            self.registers_verbose.append(
                RegisterInterval(
                    register_interval[RegistersKey.FCODE.value],
                    register_interval[RegistersKey.START_REGISTER.value],
                    register_interval[RegistersKey.NUM_OF_REGISTERS.value]
                )
            )

        for register_interval in inverter_profile[ProfileKey.REGISTERS.value]:
            self.registers.append(
                RegisterInterval(register_interval[RegistersKey.FCODE.value],
                                 register_interval[RegistersKey.START_REGISTER.value],
                                 register_interval[RegistersKey.NUM_OF_REGISTERS.value])
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
