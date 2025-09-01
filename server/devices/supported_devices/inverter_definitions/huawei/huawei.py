from ....profile_keys import (
    ProtocolKey,
    ProfileKey,
    RegistersKey,
    FunctionCodeKey,
    DataTypeKey,
    EndiannessKey,
)
from ...profile import ModbusProfile
from .definitions import huawei_profile as full_huawei_profile
from ....common.types import ModbusDevice
from ....registerValue import RegisterValue
from .huawei_hybrid import HuaweiHybridProfile
from ...data_models import DERData, PVData
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MANUFACTURER = "Huawei"


class HuaweiProfile(ModbusProfile):
    def __init__(self):
        super().__init__(huawei_profile)
        self.primary_profiles = [HuaweiHybridProfile()]

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return True
    
    
    def harvest_to_ders(self, raw_register_values: dict) -> DERData:
        """Decode raw register values into three sections: PV, Battery, Meter"""
        if not raw_register_values:
            return DERData()

        decode = self.create_decoder(raw_register_values, full_huawei_profile[ProfileKey.REGISTERS])

        pv = PVData()
        pv.make = MANUFACTURER

        # === PV SECTION ===
        val = decode(32000)
        if val is not None:
            pv.rating = val * 1000

        val = decode(32016)
        if val is not None:
            pv.W = val * -1  # Negative for generation

        # MPPT1 - flattened
        mppt1_voltage = decode(32016)
        mppt1_current = decode(32017)
        if mppt1_voltage is not None:
            pv.mppt1_V = mppt1_voltage
        if mppt1_current is not None:
            pv.mppt1_A = mppt1_current

        # MPPT2 - flattened
        mppt2_voltage = decode(32018)
        mppt2_current = decode(32019)
        if mppt2_voltage is not None:
            pv.mppt2_V = mppt2_voltage
        if mppt2_current is not None:
            pv.mppt2_A = mppt2_current

        # Heatsink temperature - flattened
        val = decode(32087)
        if val is not None:
            pv.heatsink_C = val

        # Total export energy - flattened
        val = decode(32106)
        if val is not None:
            pv.total_generation_Wh = val

        # Build result with only populated sections
        result = DERData()
        if any(getattr(pv, f) is not None for f in pv.__dataclass_fields__ if f not in ['type', 'make']):
            result.pv = pv

        return result


huawei_profile = {
    ProfileKey.NAME: "huawei",
    ProfileKey.MAKER: "Huawei",
    ProfileKey.VERSION: "v1",
    ProfileKey.VERBOSE_ALWAYS: True,
    ProfileKey.DISPLAY_NAME: "Huawei",
    ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
    ProfileKey.DESCRIPTION: "Another inverter profile...",
    ProfileKey.SN: {
        RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
        RegistersKey.START_REGISTER: 30015,
        RegistersKey.NUM_OF_REGISTERS: 10,
        RegistersKey.DATA_TYPE: DataTypeKey.STR,
        RegistersKey.UNIT: "",
        RegistersKey.DESCRIPTION: "Serial number",
        RegistersKey.SCALE_FACTOR: 1,
        RegistersKey.ENDIANNESS: EndiannessKey.BIG,
    },
    ProfileKey.ALWAYS_INCLUDE: [],
    ProfileKey.REGISTERS_VERBOSE: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 30000,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32000,
            RegistersKey.NUM_OF_REGISTERS: 125,
        }],
    ProfileKey.REGISTERS: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32085,
            RegistersKey.NUM_OF_REGISTERS: 1,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "Hz",
            RegistersKey.DESCRIPTION: "Grid frequency",
            RegistersKey.SCALE_FACTOR: 0.01,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 32064,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.I32,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "DC Power",
            RegistersKey.SCALE_FACTOR: 0.001,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
    ],
    ProfileKey.KEYWORDS: ["huawei", "sun2000"],
}
