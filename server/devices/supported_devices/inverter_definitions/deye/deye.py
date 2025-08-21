from ....profile_keys import (
    ProtocolKey,
    ProfileKey,
    RegistersKey,
    FunctionCodeKey,
    DataTypeKey,
    EndiannessKey,
)
from ...profile import ModbusProfile
from ....common.types import ModbusDevice
from ....registerValue import RegisterValue
from .definitions_slim import deye_profile as slim_deye_profile
from ...data_models import (
    DERData, PVData, BatteryData, MeterData, MPPTData, PhaseData, 
    TotalEnergyData, EnergyData, SoCData, NominalData, TemperatureData, UptimeData
)
import logging


# Constants
MANUFACTURER = "Deye"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DeyeProfile(ModbusProfile):
    def __init__(self):
        super().__init__(deye_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return True

    def dict_to_ders(self, raw_register_values: dict) -> DERData:
        """Decode raw register values into three sections: PV, Battery, Meter"""
        if not raw_register_values:
            return DERData()

        reg_defs = {entry[RegistersKey.START_REGISTER]: entry for entry in slim_deye_profile[ProfileKey.REGISTERS]}
        is_high_voltage = raw_register_values.get(0) == 6

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

        def scale_voltage(val: float) -> float:
            return val * (0.1 if is_high_voltage else 0.01)

        def scale_power(val: float) -> float:
            return val * (10 if is_high_voltage else 1)

        # Create data objects
        import time
        timestamp = int(time.time() * 1000)  # Current timestamp in milliseconds
        
        pv = PVData()
        pv.ts = timestamp
        pv.make = MANUFACTURER  # Set manufacturer
        battery = BatteryData()
        battery.ts = timestamp
        battery.make = MANUFACTURER  # Set manufacturer
        meter = MeterData()
        meter.ts = timestamp
        meter.make = MANUFACTURER  # Set manufacturer

        # === PV SECTION - Simple direct assignment ===
        val = decode(20)
        if val is not None:
            pv.rated_power = val
            
        # PV Power (sum of pv1-4)
        pv_power_vals = [decode(addr) for addr in [672, 673, 674, 675]]
        if any(v is not None for v in pv_power_vals):
            total = sum(v for v in pv_power_vals if v is not None) * -1
            pv.W = scale_power(total)

        # MPPT1
        mppt1_voltage = decode(676)
        mppt1_current = decode(677)
        if mppt1_voltage is not None or mppt1_current is not None:
            pv.MPPT1 = MPPTData()
            if mppt1_voltage is not None:
                pv.MPPT1.V = mppt1_voltage
            if mppt1_current is not None:
                pv.MPPT1.A = mppt1_current * -1
        
        # MPPT2
        mppt2_voltage = decode(678)
        mppt2_current = decode(679)
        if mppt2_voltage is not None or mppt2_current is not None:
            pv.MPPT2 = MPPTData()
            if mppt2_voltage is not None:
                pv.MPPT2.V = mppt2_voltage
            if mppt2_current is not None:
                pv.MPPT2.A = mppt2_current * -1
        
        val = decode(541)
        if val is not None:
            pv.heatsink_tmp = TemperatureData()
            pv.heatsink_tmp.C = val
        
        val = decode(534)
        if val is not None:
            if pv.total is None:
                pv.total = TotalEnergyData()
            if pv.total.export is None:
                pv.total.export = EnergyData()
            pv.total.export.Wh = val * 1000

        # === BATTERY SECTION - Simple direct assignment ===
        val = decode(590)
        if val is not None:
            battery.W = scale_power(val) * -1
        
        val = decode(591)
        if val is not None:
            battery.A = val * -1
        
        val = decode(587)
        if val is not None:
            battery.V = scale_voltage(val)
        
        val = decode(588)
        if val is not None:
            battery.SoC = SoCData()
            battery.SoC.nom = NominalData()
            battery.SoC.nom.fract = val / 100.0  # Convert percentage to fraction
        
        val = decode(516)
        if val is not None:
            if battery.total is None:
                battery.total = TotalEnergyData()
            if battery.total.import_ is None:
                battery.total.import_ = EnergyData()
            battery.total.import_.Wh = val * 1000
        
        val = decode(518)
        if val is not None:
            if battery.total is None:
                battery.total = TotalEnergyData()
            if battery.total.export is None:
                battery.total.export = EnergyData()
            battery.total.export.Wh = val * 1000
        
        # Battery temperature (special calculation)
        temp_raw = decode(217)
        if temp_raw is not None:
            temp = (temp_raw - 1000.0) / 10.0
            battery.Tmp = TemperatureData()
            battery.Tmp.C = temp

        # === METER SECTION - Simple direct assignment ===
        val = decode(619)
        if val is not None:
            meter.W = val
        
        val = decode(609)
        if val is not None:
            meter.Hz = val
        
        val = decode(522)
        if val is not None:
            if meter.total is None:
                meter.total = TotalEnergyData()
            if meter.total.import_ is None:
                meter.total.import_ = EnergyData()
            meter.total.import_.Wh = val * 1000
        
        val = decode(524)
        if val is not None:
            if meter.total is None:
                meter.total = TotalEnergyData()
            if meter.total.export is None:
                meter.total.export = EnergyData()
            meter.total.export.Wh = val * 1000
        
        # L1 phase
        l1_voltage = decode(598)
        l1_current = decode(610)
        l1_power = decode(616)
        if l1_voltage is not None or l1_current is not None or l1_power is not None:
            meter.L1 = PhaseData()
            if l1_voltage is not None:
                meter.L1.V = l1_voltage
            if l1_current is not None:
                meter.L1.A = l1_current * -1
            if l1_power is not None:
                meter.L1.W = l1_power
        
        # L2 phase
        l2_voltage = decode(599)
        l2_current = decode(611)
        l2_power = decode(617)
        if l2_voltage is not None or l2_current is not None or l2_power is not None:
            meter.L2 = PhaseData()
            if l2_voltage is not None:
                meter.L2.V = l2_voltage
            if l2_current is not None:
                meter.L2.A = l2_current * -1
            if l2_power is not None:
                meter.L2.W = l2_power
        
        # L3 phase
        l3_voltage = decode(600)
        l3_current = decode(612)
        l3_power = decode(618)
        if l3_voltage is not None or l3_current is not None or l3_power is not None:
            meter.L3 = PhaseData()
            if l3_voltage is not None:
                meter.L3.V = l3_voltage
            if l3_current is not None:
                meter.L3.A = l3_current * -1
            if l3_power is not None:
                meter.L3.W = l3_power

        # Build result with only populated sections
        result = DERData()
        if any(getattr(pv, f) is not None for f in pv.__dataclass_fields__ if f != 'name'):
            result.pv = pv
        if any(getattr(battery, f) is not None for f in battery.__dataclass_fields__ if f != 'name'):
            result.battery = battery
        if any(getattr(meter, f) is not None for f in meter.__dataclass_fields__ if f != 'name'):
            result.meter = meter

        return result


deye_profile = {
    ProfileKey.NAME: "deye",
    ProfileKey.MAKER: "Deye",
    ProfileKey.VERSION: "V1.1b3",
    ProfileKey.VERBOSE_ALWAYS: True,
    ProfileKey.DISPLAY_NAME: "Deye",
    ProfileKey.PROTOCOL: ProtocolKey.SOLARMAN,
    ProfileKey.DESCRIPTION: "Another inverter profile...",
    ProfileKey.SN: {
        RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
        RegistersKey.START_REGISTER: 3,
        RegistersKey.NUM_OF_REGISTERS: 8,
        RegistersKey.DATA_TYPE: DataTypeKey.STR,
        RegistersKey.UNIT: "",
        RegistersKey.DESCRIPTION: "Serial number",
        RegistersKey.SCALE_FACTOR: 1,
        RegistersKey.ENDIANNESS: EndiannessKey.BIG,
    },
    ProfileKey.ALWAYS_INCLUDE: [0],
    ProfileKey.REGISTERS_VERBOSE: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 0,
            RegistersKey.NUM_OF_REGISTERS: 59,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 60,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 185,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 310,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 435,
            RegistersKey.NUM_OF_REGISTERS: 64,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 500,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 625,
            RegistersKey.NUM_OF_REGISTERS: 125,
        }
    ],
    ProfileKey.REGISTERS: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 609,
            RegistersKey.NUM_OF_REGISTERS: 1,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "Hz",
            RegistersKey.DESCRIPTION: "Grid frequency",
            RegistersKey.SCALE_FACTOR: 0.01,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 672,
            RegistersKey.NUM_OF_REGISTERS: 4,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "DC Power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
    ],
    ProfileKey.KEYWORDS: ["deye", "high-flying"],
}
