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
from ...data_models import DERData, PVData, BatteryData, MeterData, Value, Unit, MPPTData, PhaseData
import logging


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

        def make_value(val: float, unit: Unit, name: str) -> Value:
            return Value(value=val, unit=unit, name=name)

        # Create data objects
        pv = PVData()
        battery = BatteryData()
        meter = MeterData()

        # === PV SECTION - Simple direct assignment ===
        val = decode(20)
        if val is not None:
            pv.rated_power = make_value(val, Unit.W, "Rated Power")
            
        # PV Power (sum of pv1-4)
        pv_power_vals = [decode(addr) for addr in [672, 673, 674, 675]]
        if any(v is not None for v in pv_power_vals):
            total = sum(v for v in pv_power_vals if v is not None) * -1
            pv.power = make_value(scale_power(total), Unit.W, "PV Power")

        # MPPT1
        mppt1_voltage = decode(676)
        mppt1_current = decode(677)
        if mppt1_voltage is not None or mppt1_current is not None:
            pv.mppt1 = MPPTData()
            if mppt1_voltage is not None:
                pv.mppt1.voltage = make_value(mppt1_voltage, Unit.V, "MPPT1 Voltage")
            if mppt1_current is not None:
                pv.mppt1.current = make_value(mppt1_current * -1, Unit.A, "MPPT1 Current")
        
        # MPPT2
        mppt2_voltage = decode(678)
        mppt2_current = decode(679)
        if mppt2_voltage is not None or mppt2_current is not None:
            pv.mppt2 = MPPTData()
            if mppt2_voltage is not None:
                pv.mppt2.voltage = make_value(mppt2_voltage, Unit.V, "MPPT2 Voltage")
            if mppt2_current is not None:
                pv.mppt2.current = make_value(mppt2_current * -1, Unit.A, "MPPT2 Current")
        
        val = decode(541)
        if val is not None:
            pv.inverter_temperature = make_value(val, Unit.C, "Inverter Temperature")
        
        val = decode(534)
        if val is not None:
            pv.total_pv_generation = make_value(val * 1000, Unit.Wh, "Total PV Generation")

        # === BATTERY SECTION - Simple direct assignment ===
        val = decode(590)
        if val is not None:
            battery.power = make_value(scale_power(val) * -1, Unit.W, "Battery Power")
        
        val = decode(591)
        if val is not None:
            battery.current = make_value(val * -1, Unit.A, "Battery Current")
        
        val = decode(587)
        if val is not None:
            battery.voltage = make_value(scale_voltage(val), Unit.V, "Battery Voltage")
        
        val = decode(588)
        if val is not None:
            battery.soc = make_value(val, Unit.PERCENT, "Battery SOC")
        
        val = decode(516)
        if val is not None:
            battery.total_charge_energy = make_value(val * 1000, Unit.Wh, "Total Charge Energy")
        
        val = decode(518)
        if val is not None:
            battery.total_discharge_energy = make_value(val * 1000, Unit.Wh, "Total Discharge Energy")
        
        # Battery temperature (special calculation)
        temp_raw = decode(217)
        if temp_raw is not None:
            temp = (temp_raw - 1000.0) / 10.0
            battery.battery_temperature = make_value(temp, Unit.C, "Battery Temperature")

        # === METER SECTION - Simple direct assignment ===
        val = decode(619)
        if val is not None:
            meter.active_power = make_value(val, Unit.W, "Active Power")
        
        val = decode(609)
        if val is not None:
            meter.frequency = make_value(val, Unit.Hz, "Grid Frequency")
        
        val = decode(522)
        if val is not None:
            meter.total_import_energy = make_value(val * 1000, Unit.Wh, "Total Import Energy")
        
        val = decode(524)
        if val is not None:
            meter.total_export_energy = make_value(val * 1000, Unit.Wh, "Total Export Energy")
        
        # L1 phase
        l1_voltage = decode(598)
        l1_current = decode(610)
        l1_power = decode(616)
        if l1_voltage is not None or l1_current is not None or l1_power is not None:
            meter.l1 = PhaseData()
            if l1_voltage is not None:
                meter.l1.voltage = make_value(l1_voltage, Unit.V, "L1 Voltage")
            if l1_current is not None:
                meter.l1.current = make_value(l1_current * -1, Unit.A, "L1 Current")
            if l1_power is not None:
                meter.l1.active_power = make_value(l1_power, Unit.W, "L1 Active Power")
        
        # L2 phase
        l2_voltage = decode(599)
        l2_current = decode(611)
        l2_power = decode(617)
        if l2_voltage is not None or l2_current is not None or l2_power is not None:
            meter.l2 = PhaseData()
            if l2_voltage is not None:
                meter.l2.voltage = make_value(l2_voltage, Unit.V, "L2 Voltage")
            if l2_current is not None:
                meter.l2.current = make_value(l2_current * -1, Unit.A, "L2 Current")
            if l2_power is not None:
                meter.l2.active_power = make_value(l2_power, Unit.W, "L2 Active Power")
        
        # L3 phase
        l3_voltage = decode(600)
        l3_current = decode(612)
        l3_power = decode(618)
        if l3_voltage is not None or l3_current is not None or l3_power is not None:
            meter.l3 = PhaseData()
            if l3_voltage is not None:
                meter.l3.voltage = make_value(l3_voltage, Unit.V, "L3 Voltage")
            if l3_current is not None:
                meter.l3.current = make_value(l3_current * -1, Unit.A, "L3 Current")
            if l3_power is not None:
                meter.l3.active_power = make_value(l3_power, Unit.W, "L3 Active Power")

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
