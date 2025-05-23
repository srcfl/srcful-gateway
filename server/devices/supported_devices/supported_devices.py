from ..profile_keys import DeviceCategoryKey
from .base_definition import BaseDefinition

# Inverter definitions
from .inverter_definitions.huawei import HuaweiDefinition
from .inverter_definitions.solaredge import SolarEdgeDefinition
from .inverter_definitions.solaredge_us import SolarEdgeUsDefinition
from .inverter_definitions.sungrow import SungrowDefinition
from .inverter_definitions.sungrow_sf import SungrowSFDefinition
from .inverter_definitions.sma import SmaDefinition
from .inverter_definitions.fronius import FroniusDefinition
from .inverter_definitions.fronius_sf import FroniusSFDefinition
from .inverter_definitions.deye import DeyeDefinition
from .inverter_definitions.deye_micro import DeyeMicroDefinition
from .inverter_definitions.growatt import GrowattDefinition
from .inverter_definitions.goodwe import GoodWeDefinition
from .inverter_definitions.ferroamp import FerroampDefinition
from .inverter_definitions.sofar import SofarDefinition
from .inverter_definitions.solis import SolisDefinition
from .inverter_definitions.solis_hybrid import SolisHybridDefinition
from .inverter_definitions.solax import SolaxDefinition
from .inverter_definitions.unknown import UnknownDefinition

# Meter definitions
from .meter_definitions.lqt40s import Lqt40sDefinition
from .meter_definitions.sdm630 import Sdm630Definition


supported_devices: list[BaseDefinition] = [
    HuaweiDefinition(),
    SolarEdgeDefinition(),
    SolarEdgeUsDefinition(),
    SungrowDefinition(),
    SungrowSFDefinition(),
    SmaDefinition(),
    FroniusDefinition(),
    FroniusSFDefinition(),
    DeyeDefinition(),
    DeyeMicroDefinition(),
    GrowattDefinition(),
    GoodWeDefinition(),
    FerroampDefinition(),
    SofarDefinition(),
    SolisDefinition(),
    SolisHybridDefinition(),
    SolaxDefinition(),
    UnknownDefinition(),

    Lqt40sDefinition(),
    Sdm630Definition(),
]
