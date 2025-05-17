from ..profile_keys import DeviceCategoryKey

# Inverter definitions
from .inverter_definitions.huawei import huawei_profile
from .inverter_definitions.solaredge import solaredge_profile
from .inverter_definitions.solaredge_us import solaredge_us_profile
from .inverter_definitions.sungrow import sungrow_profile
from .inverter_definitions.sungrow_sf import sungrow_sf_profile
from .inverter_definitions.sma import sma_profile
from .inverter_definitions.fronius import fronius_profile
from .inverter_definitions.fronius_sf import fronius_sf_profile
from .inverter_definitions.deye import deye_profile
from .inverter_definitions.deye_micro import deye_micro_profile
from .inverter_definitions.growatt import growatt_profile
from .inverter_definitions.goodwe import goodwe_profile
from .inverter_definitions.ferroamp import ferroamp_profile
from .inverter_definitions.sofar import sofar_profile
from .inverter_definitions.solis import solis_profile
from .inverter_definitions.solis_hybrid import solis_hybrid_profile
from .inverter_definitions.solax import solax_profile
from .inverter_definitions.unknown import unknown_profile

# Meter definitions
from .meter_definitions.lqt40s import lqt40s_profile
from .meter_definitions.sdm630 import sdm630_profile


supported_devices = {
    DeviceCategoryKey.INVERTERS: [
        huawei_profile,
        solaredge_profile,
        solaredge_us_profile,
        sungrow_profile,
        sungrow_sf_profile,
        sma_profile,
        fronius_profile,
        fronius_sf_profile,
        deye_profile,
        deye_micro_profile,
        growatt_profile,
        goodwe_profile,
        ferroamp_profile,
        sofar_profile,
        solis_profile,
        solis_hybrid_profile,
        solax_profile,
        unknown_profile,
    ],
    DeviceCategoryKey.METERS: [
        lqt40s_profile,
        sdm630_profile,
    ],
}
