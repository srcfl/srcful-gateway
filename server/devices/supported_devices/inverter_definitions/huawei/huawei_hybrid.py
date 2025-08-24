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
from ...data_models import DERData, PVData, BatteryData, MeterData
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MANUFACTURER = "Huawei"

class HuaweiHybridProfile(ModbusProfile):
    def __init__(self):
        super().__init__(huawei_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return self._has_valid_SoC(device) and self._battery_has_voltage(device)

    def _has_valid_SoC(self, device: ModbusDevice) -> float:
        battery_SoC = RegisterValue(address=37004,
                                    size=1,
                                    function_code=FunctionCodeKey.READ_HOLDING_REGISTERS,
                                    data_type=DataTypeKey.U16,
                                    scale_factor=0.1,
                                    endianness=EndiannessKey.BIG)

        _, _, value = battery_SoC.read_value(device)

        logger.info(f"Battery SoC: {value}%")

        return value != None and 1 <= value <= 100

    def _battery_has_voltage(self, device: ModbusDevice) -> bool:
        battery_voltage = RegisterValue(address=37763,
                                        size=2,
                                        function_code=FunctionCodeKey.READ_HOLDING_REGISTERS,
                                        data_type=DataTypeKey.U16,
                                        scale_factor=0.1,
                                        endianness=EndiannessKey.BIG)

        _, _, value = battery_voltage.read_value(device)

        logger.info(f"Battery voltage: {value}V")

        return value != None and value > 0
    
    
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
        
        pv = PVData()
        pv.make = MANUFACTURER
        
        battery = BatteryData()
        battery.make = MANUFACTURER 
        
        meter = MeterData()
        meter.make = MANUFACTURER

        # === PV SECTION ===
        
        val = decode(30073)
        if val is not None:
            pv.rating = val * 1000
        
        val = decode(32064)
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
        val = decode(13002)
        if val is not None:
            pv.total_export_Wh = val

        # === BATTERY SECTION - Flattened structure ===
        val = decode(37001)
        if val is not None:
            battery.W = val
            
        val = decode(37021)
        if val is not None:
            battery.A = val
        
        val = decode(37003)
        if val is not None:
            battery.V = val

        # Battery temperature - flattened
        val = decode(37022)
        if val is not None:
            battery.heatsink_C = val

        # State of Charge - flattened
        val = decode(37004)
        if val is not None:
            battery.SoC_nom_fract = val / 100.0  # Convert percentage to fraction
            
        # Battery energy totals - flattened
        val = decode(37066)
        if val is not None:
            battery.total_import_Wh = val * 1000
            
        val = decode(37068)
        if val is not None:
            battery.total_import_Wh = val * 1000
            
        # === METER SECTION - Flattened structure ===
        
        # L1 phase - flattened
        l1_voltage = decode(37101)
        l1_current = decode(37107)
        l1_power = decode(37132)
        if l1_voltage is not None:
            meter.L1_V = l1_voltage
        if l1_current is not None:
            meter.L1_A = l1_current * -1
        if l1_power is not None:
            meter.L1_W = l1_power
        
        # L2 phase - flattened
        l2_voltage = decode(37103)
        l2_current = decode(37109)
        l2_power = decode(37134)
        if l2_voltage is not None:
            meter.L2_V = l2_voltage
        if l2_current is not None:
            meter.L2_A = l2_current * -1
        if l2_power is not None:
            meter.L2_W = l2_power
        
        # L3 phase - flattened
        l3_voltage = decode(37105)
        l3_current = decode(37111)
        l3_power = decode(37136)
        if l3_voltage is not None:
            meter.L3_V = l3_voltage
        if l3_current is not None:
            meter.L3_A = l3_current * -1
        if l3_power is not None:
            meter.L3_W = l3_power
            
        # Meter totals - flattened   
        val = decode(37113)
        if val is not None:
            meter.W = val * -1
        
        val = decode(37118)
        if val is not None:
            meter.Hz = val
        
        # Meter energy totals - flattened
        val = decode(37119)
        if val is not None:
            meter.total_import_Wh = val * 1000
        
        val = decode(37121)
        if val is not None:
            meter.total_export_Wh = val * 1000
        

        # Build result with only populated sections
        result = DERData()
        if any(getattr(pv, f) is not None for f in pv.__dataclass_fields__ if f not in ['type', 'make']):
            result.pv = pv
        if any(getattr(battery, f) is not None for f in battery.__dataclass_fields__ if f not in ['type', 'make']):
            result.battery = battery
        if any(getattr(meter, f) is not None for f in meter.__dataclass_fields__ if f not in ['type', 'make']):
            result.meter = meter

        return result


huawei_profile = {
    ProfileKey.NAME: "huawei_hybrid",
    ProfileKey.MAKER: "Huawei",
    ProfileKey.VERSION: "V1.1b3",
    ProfileKey.VERBOSE_ALWAYS: True,
    ProfileKey.DISPLAY_NAME: "Huawei Hybrid",
    ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
    ProfileKey.DESCRIPTION: "Huawei Hybrid inverter profile...",
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
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 37000,
            RegistersKey.NUM_OF_REGISTERS: 69,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 37700,
            RegistersKey.NUM_OF_REGISTERS: 100,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47000,
            RegistersKey.NUM_OF_REGISTERS: 1,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47028,
            RegistersKey.NUM_OF_REGISTERS: 62,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47100,
            RegistersKey.NUM_OF_REGISTERS: 10,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47242,
            RegistersKey.NUM_OF_REGISTERS: 9,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47299,
            RegistersKey.NUM_OF_REGISTERS: 1,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47415,
            RegistersKey.NUM_OF_REGISTERS: 20,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47590,
            RegistersKey.NUM_OF_REGISTERS: 2,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47604,
            RegistersKey.NUM_OF_REGISTERS: 2,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 47750,
            RegistersKey.NUM_OF_REGISTERS: 6,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 37100,
            RegistersKey.NUM_OF_REGISTERS: 39,
        }
    ],
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
