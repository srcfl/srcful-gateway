# To add a new inverter, create a new file in the inverters folder and import it here
# Then add the new inverter to the inverters list and it will be supported by the gateway (PoS)
import typing
from ..enums import ProfileKey, RegistersKey, OperationKey
from .inverters.sungrow import profile as sungrow
from .inverters.sungrow_hybrid import profile as sungrow_hybrid
from .inverters.solaredge import profile as solaredge
from .inverters.growatt import profile as growatt
from .inverters.huawei import profile as huawei
from .inverters.lqt40s import profile as lqt40s

inverters = [sungrow, sungrow_hybrid, solaredge, growatt, huawei, lqt40s]


class RegisterInterval:
    def __init__(self, operation, start_register, offset):
        self.operation = operation
        self.start_register = start_register
        self.offset = offset


class InverterProfile:
    def __init__(self, inverter_profile):
        self.name = inverter_profile[ProfileKey.NAME]
        self.registers = []

        for register_intervall in inverter_profile[ProfileKey.REGISTERS]:
            self.registers.append(
                RegisterInterval(register_intervall[RegistersKey.OPERATION],
                                 register_intervall[RegistersKey.START_REGISTER],
                                 register_intervall[RegistersKey.NUM_OF_REGISTERS])
            )

    def get_registers(self) -> typing.List[RegisterInterval]:
        return self.registers


class InverterProfiles:
    def __init__(self):
        self.profiles = []

        for inverter in inverters:
            self.profiles.append(InverterProfile(inverter))

    def get(self, name) -> InverterProfile:
        for profile in self.profiles:
            if profile.name == name:
                return profile
        return None

    def get_supported_inverters(self) -> typing.List[str]:
        return [profile.name for profile in self.profiles]
