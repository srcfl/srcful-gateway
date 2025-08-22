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
from ...data_models import (
    DERData, PVData, MPPTData, TotalEnergyData, EnergyData, TemperatureData
)
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
    
    
    def dict_to_ders(self, raw_register_values: dict) -> DERData:
        """Decode raw register values into three sections: PV, Battery, Meter"""
        if not raw_register_values:
            return DERData()

        reg_defs = {entry[RegistersKey.START_REGISTER]: entry for entry in full_huawei_profile[ProfileKey.REGISTERS]}

        def decode(addr: int) -> float | int | None:
            entry = reg_defs.get(addr)
            if not entry:
                return None
            size = entry[RegistersKey.NUM_OF_REGISTERS]
            try:
                regs = [raw_register_values[addr + i] for i in range(size)]
            except KeyError:
                return None
            raw = bytearray()
            for r in regs:
                raw.extend(int(r).to_bytes(2, "big", signed=False))
            rv = RegisterValue(addr,
                               size,
                               entry[RegistersKey.FUNCTION_CODE],
                               entry[RegistersKey.DATA_TYPE],
                               entry[RegistersKey.SCALE_FACTOR],
                               entry[RegistersKey.ENDIANNESS])
            _, value = rv._interpret_value(raw)
            return value

        # Create data objects
        import time
        timestamp = int(time.time() * 1000)  # Current timestamp in milliseconds
        
        pv = PVData()
        pv.ts = timestamp
        pv.make = MANUFACTURER
        

        # === PV SECTION ===
        
        val = decode(30073)
        if val is not None:
            pv.rated_power = val * 1000
        
        val = decode(32064)
        if val is not None:
            pv.W = val * -1  # Negative for generation
            
        # MPPT1
        mppt1_voltage = decode(32016)
        mppt1_current = decode(32017)
        if mppt1_voltage is not None or mppt1_current is not None:
            pv.MPPT1 = MPPTData()
            if mppt1_voltage is not None:
                pv.MPPT1.V = mppt1_voltage
            if mppt1_current is not None:
                pv.MPPT1.A = mppt1_current
        
        # MPPT2
        mppt2_voltage = decode(32018)
        mppt2_current = decode(32019)
        if mppt2_voltage is not None or mppt2_current is not None:
            pv.MPPT2 = MPPTData()
            if mppt2_voltage is not None:
                pv.MPPT2.V = mppt2_voltage 
            if mppt2_current is not None:
                pv.MPPT2.A = mppt2_current
            
        val = decode(32087)
        if val is not None:
            pv.heatsink_tmp = TemperatureData()
            pv.heatsink_tmp.C = val
            
            
        val = decode(13002)
        if val is not None:
            if pv.total is None:
                pv.total = TotalEnergyData()
            if pv.total.export is None:
                pv.total.export = EnergyData()
            pv.total.export.Wh = val

        # Build result with only populated sections
        result = DERData()
        if any(getattr(pv, f) is not None for f in pv.__dataclass_fields__ if f not in ['type', 'make']):
            result.pv = pv

        return result


huawei_profile = {
    ProfileKey.NAME: "huawei",
    ProfileKey.MAKER: "Huawei",
    ProfileKey.VERSION: "V1.1b3",
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
