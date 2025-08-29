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
from .definitions import deye_profile as full_deye_profile
from ...data_models import DERData, PVData, BatteryData, MeterData
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
    
    def harvest_to_decoded_dict(self, raw_register_values: dict) -> dict:
        decode = self.create_decoder(raw_register_values, full_deye_profile[ProfileKey.REGISTERS])
        
        registers = {}
        
        inv_output_total_active_power = decode(636)
        battery_output_power = decode(590)
        grid_active_power = decode(607)

        # for register in full_deye_profile[ProfileKey.REGISTERS]:
        #     val = decode(register.get(RegistersKey.START_REGISTER))
            
        #     if val is not None:
        #         registers[register.get(RegistersKey.START_REGISTER)] = {
        #             "name": register.get(RegistersKey.NAME, ""),
        #             "value": val,
        #             "description": register.get(RegistersKey.DESCRIPTION, ""),
        #         }

        return {"registers": registers}

    def harvest_to_ders(self, raw_register_values: dict) -> DERData:
        """Decode raw register values into three sections: PV, Battery, Meter"""
        if not raw_register_values:
            return DERData()

        decode = self.create_decoder(raw_register_values, full_deye_profile[ProfileKey.REGISTERS])
        is_high_voltage = decode(0) == 6

        def scale_voltage(val: float) -> float:
            return val * (0.1 if is_high_voltage else 0.01)

        def scale_power(val: float) -> float:
            return val * (10 if is_high_voltage else 1)

        pv = PVData()
        pv.make = MANUFACTURER  # Set manufacturer
        battery = BatteryData()
        battery.make = MANUFACTURER  # Set manufacturer
        meter = MeterData()
        meter.make = MANUFACTURER  # Set manufacturer

        # === PV SECTION - Simple direct assignment ===
        val = decode(20)
        if val is not None:
            pv.rating = val

        # PV Power (sum of pv1-4)
        pv_power_vals = [decode(addr) for addr in [672, 673, 674, 675]]
        if any(v is not None for v in pv_power_vals):
            total = sum(v for v in pv_power_vals if v is not None) * -1
            pv.W = scale_power(total)

        # MPPT1 - flattened
        mppt1_voltage = decode(676)
        mppt1_current = decode(677)
        if mppt1_voltage is not None:
            pv.mppt1_V = mppt1_voltage
        if mppt1_current is not None:
            pv.mppt1_A = mppt1_current * -1

        # MPPT2 - flattened
        mppt2_voltage = decode(678)
        mppt2_current = decode(679)
        if mppt2_voltage is not None:
            pv.mppt2_V = mppt2_voltage
        if mppt2_current is not None:
            pv.mppt2_A = mppt2_current * -1

        # Heatsink temperature - flattened
        val = decode(541)
        if val is not None:
            pv.heatsink_C = val

        # Total export energy - flattened
        val = decode(534)
        if val is not None:
            pv.total_export_Wh = val * 1000

        # === BATTERY SECTION - Flattened structure ===
        val = decode(590)
        if val is not None:
            battery.W = scale_power(val) * -1

        val = decode(591)
        if val is not None:
            battery.A = val * -1

        val = decode(587)
        if val is not None:
            battery.V = scale_voltage(val)

        # State of Charge - flattened
        val = decode(588)
        if val is not None:
            battery.SoC_nom_fract = val / 100.0  # Convert percentage to fraction

        # Battery energy totals - flattened
        val = decode(516)
        if val is not None:
            battery.total_import_Wh = val * 1000

        val = decode(518)
        if val is not None:
            battery.total_export_Wh = val * 1000

        # Battery temperature (special calculation) - flattened
        temp_raw = decode(217)
        if temp_raw is not None:
            temp = (temp_raw - 1000.0) / 10.0
            battery.heatsink_C = temp

        # === METER SECTION - Flattened structure ===
        val = decode(619)
        if val is not None:
            meter.W = val

        val = decode(609)
        if val is not None:
            meter.Hz = val

        # Meter energy totals - flattened
        val = decode(522)
        if val is not None:
            meter.total_import_Wh = val * 1000

        val = decode(524)
        if val is not None:
            meter.total_export_Wh = val * 1000

        # L1 phase - flattened
        l1_voltage = decode(598)
        l1_current = decode(610)
        l1_power = decode(622)
        if l1_voltage is not None:
            meter.L1_V = l1_voltage
        if l1_current is not None:
            meter.L1_A = l1_current
        if l1_power is not None:
            meter.L1_W = l1_power

        # L2 phase - flattened
        l2_voltage = decode(599)
        l2_current = decode(611)
        l2_power = decode(623)
        if l2_voltage is not None:
            meter.L2_V = l2_voltage
        if l2_current is not None:
            meter.L2_A = l2_current
        if l2_power is not None:
            meter.L2_W = l2_power

        # L3 phase - flattened
        l3_voltage = decode(600)
        l3_current = decode(612)
        l3_power = decode(624)
        if l3_voltage is not None:
            meter.L3_V = l3_voltage
        if l3_current is not None:
            meter.L3_A = l3_current
        if l3_power is not None:
            meter.L3_W = l3_power

        # Build result with only populated sections
        result = DERData()
        if any(getattr(pv, f) is not None for f in pv.__dataclass_fields__ if f not in ['type', 'make']):
            result.pv = pv
        if any(getattr(battery, f) is not None for f in battery.__dataclass_fields__ if f not in ['type', 'make']):
            result.battery = battery
        if any(getattr(meter, f) is not None for f in meter.__dataclass_fields__ if f not in ['type', 'make']):
            result.meter = meter

        return result


deye_profile = {
    ProfileKey.NAME: "deye",
    ProfileKey.MAKER: "Deye",
    ProfileKey.VERSION: "v1",
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
