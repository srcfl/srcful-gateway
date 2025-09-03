from .profile import ModbusProfile

# Inverter definitions
from .inverter_definitions.huawei.huawei import HuaweiProfile
from .inverter_definitions.huawei.huawei_hybrid import HuaweiHybridProfile
from .inverter_definitions.solaredge import SolarEdgeProfile
from .inverter_definitions.solaredge_us import SolarEdgeUsProfile
from .inverter_definitions.sungrow.sungrow import SungrowProfile
from .inverter_definitions.sungrow.sungrow_sf import SungrowSFProfile
from .inverter_definitions.sma import SmaProfile
from .inverter_definitions.fronius import FroniusProfile
from .inverter_definitions.fronius_sf import FroniusSFProfile
from .inverter_definitions.deye.deye import DeyeProfile
from .inverter_definitions.deye_micro import DeyeMicroProfile
from .inverter_definitions.growatt import GrowattProfile
from .inverter_definitions.goodwe import GoodWeProfile
from .inverter_definitions.ferroamp import FerroampProfile
from .inverter_definitions.sofar import SofarProfile
from .inverter_definitions.solis import SolisProfile
from .inverter_definitions.solis_hybrid import SolisHybridProfile
from .inverter_definitions.solax import SolaxProfile
from .inverter_definitions.unknown import UnknownProfile

# Meter definitions
from .meter_definitions.lqt40s import Lqt40sProfile
from .meter_definitions.sdm630 import Sdm630Profile


supported_devices_profiles: list[ModbusProfile] = [
    HuaweiProfile(),
    HuaweiHybridProfile(),
    SolarEdgeProfile(),
    SolarEdgeUsProfile(),
    SungrowProfile(),
    SungrowSFProfile(),
    SmaProfile(),
    FroniusProfile(),
    FroniusSFProfile(),
    DeyeProfile(),
    DeyeMicroProfile(),
    GrowattProfile(),
    GoodWeProfile(),
    FerroampProfile(),
    SofarProfile(),
    SolisProfile(),
    SolisHybridProfile(),
    SolaxProfile(),
    UnknownProfile(),

    Lqt40sProfile(),
    Sdm630Profile(),
]
