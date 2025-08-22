from ....profile_keys import (
    ProtocolKey,
    ProfileKey,
    RegistersKey,
    FunctionCodeKey,
    DataTypeKey,
    EndiannessKey,
)
from ...profile import ModbusProfile
from .definitions import sungrow_profile as full_sungrow_profile
from ....common.types import ModbusDevice
from ....registerValue import RegisterValue
from ...data_models import (
    DERData, PVData, BatteryData, MeterData, MPPTData, PhaseData, 
    TotalEnergyData, EnergyData, SoCData, NominalData, TemperatureData, UptimeData
)
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MANUFACTURER = "Sungrow"


class SungrowProfile(ModbusProfile):
    def __init__(self):
        super().__init__(sungrow_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return True

    def dict_to_ders(self, raw_register_values: dict) -> DERData:
        """Decode raw register values into three sections: PV, Battery, Meter"""
        if not raw_register_values:
            return DERData()

        reg_defs = {entry[RegistersKey.START_REGISTER]: entry for entry in full_sungrow_profile[ProfileKey.REGISTERS]}

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
        
        val = decode(5000)
        if val is not None:
            pv.rated_power = val * 1000
        
        val = decode(5016)
        if val is not None:
            pv.W = val * -1  # Negative for generation
            
        # MPPT1
        mppt1_voltage = decode(5010)
        mppt1_current = decode(5011)
        if mppt1_voltage is not None or mppt1_current is not None:
            pv.MPPT1 = MPPTData()
            if mppt1_voltage is not None:
                pv.MPPT1.V = mppt1_voltage
            if mppt1_current is not None:
                pv.MPPT1.A = mppt1_current
        
        # MPPT2
        mppt2_voltage = decode(5012)
        mppt2_current = decode(5013)
        if mppt2_voltage is not None or mppt2_current is not None:
            pv.MPPT2 = MPPTData()
            if mppt2_voltage is not None:
                pv.MPPT2.V = mppt2_voltage 
            if mppt2_current is not None:
                pv.MPPT2.A = mppt2_current
            
        val = decode(5007)
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
 
        # === BATTERY SECTION ===
        val = decode(13021)
        if val is not None:
            battery.W = val * -1
            
        val = decode(13020)
        if val is not None:
            battery.A = val
        
        val = decode(13019)
        if val is not None:
            battery.V = val

        val = decode(13024)
        if val is not None:
            battery.Tmp = TemperatureData()
            battery.Tmp.C = val

        val = decode(13022)
        if val is not None:
            battery.SoC = SoCData()
            battery.SoC.nom = NominalData()
            battery.SoC.nom.fract = val / 100.0  # Convert percentage to fraction
            
        val = decode(13026)
        if val is not None:
            if battery.total is None:
                battery.total = TotalEnergyData()
            if battery.total.import_ is None:
                battery.total.import_ = EnergyData()
            battery.total.import_.Wh = val * 1000
            
        val = decode(13040)
        if val is not None:
            if battery.total is None:
                battery.total = TotalEnergyData()
            if battery.total.import_ is None:
                battery.total.import_ = EnergyData()
            battery.total.import_.Wh = val * 1000
        

        # === METER SECTION ===
        
        # L1 phase
        l1_voltage = decode(5018)
        l1_current = decode(13030)
        l1_power = decode(5602)
        if l1_voltage is not None or l1_current is not None or l1_power is not None:
            meter.L1 = PhaseData()
            if l1_voltage is not None:
                meter.L1.V = l1_voltage
            if l1_current is not None:
                meter.L1.A = l1_current * -1
            if l1_power is not None:
                meter.L1.W = l1_power
        
        # L2 phase
        l2_voltage = decode(5019)
        l2_current = decode(13031)
        l2_power = decode(5604)
        if l2_voltage is not None or l2_current is not None or l2_power is not None:
            meter.L2 = PhaseData()
            if l2_voltage is not None:
                meter.L2.V = l2_voltage
            if l2_current is not None:
                meter.L2.A = l2_current * -1
            if l2_power is not None:
                meter.L2.W = l2_power
        
        # L3 phase
        l3_voltage = decode(5020)
        l3_current = decode(13032)
        l3_power = decode(5606)
        if l3_voltage is not None or l3_current is not None or l3_power is not None:
            meter.L3 = PhaseData()
            if l3_voltage is not None:
                meter.L3.V = l3_voltage
            if l3_current is not None:
                meter.L3.A = l3_current * -1
            if l3_power is not None:
                meter.L3.W = l3_power
            
            
        val = decode(13033)
        if val is not None:
            meter.W = val * -1
        
        val = decode(5035)
        if val is not None:
            meter.Hz = val
        
        val = decode(13037)
        if val is not None:
            if meter.total is None:
                meter.total = TotalEnergyData()
            if meter.total.import_ is None:
                meter.total.import_ = EnergyData()
            meter.total.import_.Wh = val * 1000
        
        val = decode(13046)
        if val is not None:
            if meter.total is None:
                meter.total = TotalEnergyData()
            if meter.total.export is None:
                meter.total.export = EnergyData()
            meter.total.export.Wh = val * 1000


        # Build result with only populated sections
        result = DERData()
        if any(getattr(pv, f) is not None for f in pv.__dataclass_fields__ if f not in ['type', 'make']):
            result.pv = pv
        if any(getattr(battery, f) is not None for f in battery.__dataclass_fields__ if f not in ['type', 'make']):
            result.battery = battery
        if any(getattr(meter, f) is not None for f in meter.__dataclass_fields__ if f not in ['type', 'make']):
            result.meter = meter

        return result


sungrow_profile = {
    ProfileKey.NAME: "sungrow",
    ProfileKey.MAKER: "Sungrow",
    ProfileKey.VERSION: "V1.1b3",
    ProfileKey.VERBOSE_ALWAYS: True,
    ProfileKey.DISPLAY_NAME: "Sungrow",
    ProfileKey.PROTOCOL: ProtocolKey.MODBUS,
    ProfileKey.DESCRIPTION: "Another inverter profile...",
    ProfileKey.SN: {
        RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
        RegistersKey.START_REGISTER: 4989,
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
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 4949,
            RegistersKey.NUM_OF_REGISTERS: 87,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5213,
            RegistersKey.NUM_OF_REGISTERS: 28,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5602,
            RegistersKey.NUM_OF_REGISTERS: 36,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6099,
            RegistersKey.NUM_OF_REGISTERS: 96,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6195,
            RegistersKey.NUM_OF_REGISTERS: 94,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6289,
            RegistersKey.NUM_OF_REGISTERS: 96,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6385,
            RegistersKey.NUM_OF_REGISTERS: 83,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6468,
            RegistersKey.NUM_OF_REGISTERS: 96,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6564,
            RegistersKey.NUM_OF_REGISTERS: 83,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6647,
            RegistersKey.NUM_OF_REGISTERS: 96,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 6743,
            RegistersKey.NUM_OF_REGISTERS: 83,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 12999,
            RegistersKey.NUM_OF_REGISTERS: 119,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 13049,
            RegistersKey.NUM_OF_REGISTERS: 51,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 33041,
            RegistersKey.NUM_OF_REGISTERS: 7,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 33147,
            RegistersKey.NUM_OF_REGISTERS: 1,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 31221,
            RegistersKey.NUM_OF_REGISTERS: 1,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 33207,
            RegistersKey.NUM_OF_REGISTERS: 2,
        },
    ],
    ProfileKey.REGISTERS: [
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5035,
            RegistersKey.NUM_OF_REGISTERS: 1,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "Hz",
            RegistersKey.DESCRIPTION: "Grid frequency",
            RegistersKey.SCALE_FACTOR: 0.1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 5016,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.U32,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "DC Power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
        {
            RegistersKey.NAME: "Total Active Power",
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 13033,
            RegistersKey.NUM_OF_REGISTERS: 2,
            RegistersKey.DATA_TYPE: DataTypeKey.I32,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "Total active power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.LITTLE,
        },
        {
            RegistersKey.NAME: "Battery Power",
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_INPUT_REGISTERS,
            RegistersKey.START_REGISTER: 13021,
            RegistersKey.NUM_OF_REGISTERS: 1,
            RegistersKey.DATA_TYPE: DataTypeKey.U16,
            RegistersKey.UNIT: "W",
            RegistersKey.DESCRIPTION: "Battery power",
            RegistersKey.SCALE_FACTOR: 1,
            RegistersKey.ENDIANNESS: EndiannessKey.BIG,
        },
    ],
    ProfileKey.KEYWORDS: ["sungrow", "Espressif"],
}
