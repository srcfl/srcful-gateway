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
from .inverters.goodwe import profile as goodwe
from .inverters.deye import profile as deye
from .inverters.deye_hybrid import profile as deye_hybrid
from .inverters.sma import profile as sma
from .inverters.fronius import profile as fronius

inverters = [sungrow, 
             sungrow_hybrid, 
             solaredge, 
             growatt, 
             huawei, 
             lqt40s, 
             goodwe, 
             deye, 
             deye_hybrid,
             sma,
             fronius]


class RegisterInterval:
    def __init__(self, operation, start_register, offset):
        self.operation = operation
        self.start_register = start_register
        self.offset = offset


class InverterProfile:
    def __init__(self, inverter_profile):
        self.name = inverter_profile[ProfileKey.NAME]
        self.display_name = inverter_profile[ProfileKey.DISPLAY_NAME]

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
            if profile.name == name.upper():
                return profile
        return None

    def get_supported_inverters(self) -> typing.List[str]:
        return [(profile.name, profile.display_name) for profile in self.profiles]
