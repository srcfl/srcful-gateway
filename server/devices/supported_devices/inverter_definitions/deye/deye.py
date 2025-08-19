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
from ...data_models import DERData, PVData, BatteryData, MeterData, Value, Unit, FieldNames
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
            rv = RegisterValue(addr, size, entry[RegistersKey.FUNCTION_CODE], 
                             entry[RegistersKey.DATA_TYPE], entry[RegistersKey.SCALE_FACTOR], 
                             entry[RegistersKey.ENDIANNESS])
            _, value = rv._interpret_value(raw)
            return value

        def scale_voltage_current(val: float) -> float:
            return val * (0.1 if is_high_voltage else 0.01)

        def scale_power(val: float) -> float:
            return val * (10 if is_high_voltage else 1)

        def make_value(val: float, unit: Unit, name: str) -> Value:
            return Value(value=val, unit=unit, name=name)

        # === PV SECTION ===
        pv = PVData()
        pv_mappings = [
            (20, FieldNames.RATED_POWER, Unit.W, None, 1),
            (676, FieldNames.MPPT1_VOLTAGE, Unit.V, scale_voltage_current, 1),
            (677, FieldNames.MPPT1_CURRENT, Unit.A, scale_voltage_current, -1),
            (678, FieldNames.MPPT2_VOLTAGE, Unit.V, scale_voltage_current, 1),
            (679, FieldNames.MPPT2_CURRENT, Unit.A, scale_voltage_current, -1),
            (541, FieldNames.INVERTER_TEMPERATURE, Unit.C, None, 1),
            (534, FieldNames.TOTAL_PV_GENERATION, Unit.kWh, None, 1),
        ]
        for addr, field_name, unit, scale_func, multiplier in pv_mappings:
            val = decode(addr)
            if val is not None:
                final_val = scale_func(val) if scale_func else val
                final_val *= multiplier
                setattr(pv, field_name, make_value(final_val, unit, field_name))
        
        # PV Power (sum of pv1-4)
        pv_power_vals = [decode(addr) for addr in [672, 673, 674, 675]]
        if any(v is not None for v in pv_power_vals):
            total = sum(v for v in pv_power_vals if v is not None) * -1
            pv.pv_power = make_value(total, Unit.W, FieldNames.PV_POWER)

        # === BATTERY SECTION ===
        battery = BatteryData()
        battery_mappings = [
            (590, FieldNames.BATTERY_POWER, Unit.W, scale_power, 1),
            (591, FieldNames.BATTERY_CURRENT, Unit.A, scale_voltage_current, 1),
            (587, FieldNames.BATTERY_VOLTAGE, Unit.V, scale_voltage_current, 1),
            (588, FieldNames.BATTERY_SOC, Unit.PERCENT, None, 1),
            (516, FieldNames.TOTAL_CHARGE_ENERGY, Unit.kWh, None, 1),
            (518, FieldNames.TOTAL_DISCHARGE_ENERGY, Unit.kWh, None, 1),
        ]
        for addr, field_name, unit, scale_func, multiplier in battery_mappings:
            val = decode(addr)
            if val is not None:
                final_val = scale_func(val) if scale_func else val
                final_val *= multiplier
                setattr(battery, field_name, make_value(final_val, unit, field_name))
        
        # Battery temperature (special calculation)
        temp_raw = decode(217)
        if temp_raw is not None:
            temp = (temp_raw - 1000.0) / 10.0
            battery.battery_temperature = make_value(temp, Unit.C, FieldNames.BATTERY_TEMPERATURE)

        # === METER SECTION ===
        meter = MeterData()
        meter_mappings = [
            (619, FieldNames.ACTIVE_POWER, Unit.W, None, 1),
            (609, FieldNames.FREQUENCY, Unit.Hz, None, 1),
            (522, FieldNames.TOTAL_IMPORT_ENERGY, Unit.kWh, None, 1),
            (524, FieldNames.TOTAL_EXPORT_ENERGY, Unit.kWh, None, 1),
            (610, FieldNames.METER_L1_CURRENT, Unit.A, scale_voltage_current, 1),
            (611, FieldNames.METER_L2_CURRENT, Unit.A, scale_voltage_current, 1),
            (612, FieldNames.METER_L3_CURRENT, Unit.A, scale_voltage_current, 1),
            (598, FieldNames.METER_L1_VOLTAGE, Unit.V, scale_voltage_current, 1),
            (599, FieldNames.METER_L2_VOLTAGE, Unit.V, scale_voltage_current, 1),
            (600, FieldNames.METER_L3_VOLTAGE, Unit.V, scale_voltage_current, 1),
            (616, FieldNames.METER_L1_ACTIVE_POWER, Unit.W, None, 1),
            (617, FieldNames.METER_L2_ACTIVE_POWER, Unit.W, None, 1),
            (618, FieldNames.METER_L3_ACTIVE_POWER, Unit.W, None, 1),
        ]
        for addr, field_name, unit, scale_func, multiplier in meter_mappings:
            val = decode(addr)
            if val is not None:
                final_val = scale_func(val) if scale_func else val
                final_val *= multiplier
                setattr(meter, field_name, make_value(final_val, unit, field_name))

        # Build result with populated sections
        result = DERData()
        
        if any(getattr(pv, f) is not None for f in pv.__dataclass_fields__):
            result.pv = pv
        if any(getattr(battery, f) is not None for f in battery.__dataclass_fields__):
            result.battery = battery
        if any(getattr(meter, f) is not None for f in meter.__dataclass_fields__):
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
