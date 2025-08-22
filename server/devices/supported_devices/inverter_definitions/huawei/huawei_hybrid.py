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
from ...data_models import (
    DERData, PVData, BatteryData, MeterData, MPPTData, PhaseData, 
    TotalEnergyData, EnergyData, SoCData, NominalData, TemperatureData, UptimeData
)
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


        # === BATTERY SECTION ===
        val = decode(37001)
        if val is not None:
            battery.W = val
            
        val = decode(37021)
        if val is not None:
            battery.A = val
        
        val = decode(37003)
        if val is not None:
            battery.V = val

        val = decode(37022)
        if val is not None:
            battery.Tmp = TemperatureData()
            battery.Tmp.C = val

        val = decode(37004)
        if val is not None:
            battery.SoC = SoCData()
            battery.SoC.nom = NominalData()
            battery.SoC.nom.fract = val / 100.0  # Convert percentage to fraction
            
        val = decode(37066)
        if val is not None:
            if battery.total is None:
                battery.total = TotalEnergyData()
            if battery.total.import_ is None:
                battery.total.import_ = EnergyData()
            battery.total.import_.Wh = val * 1000
            
        val = decode(37068)
        if val is not None:
            if battery.total is None:
                battery.total = TotalEnergyData()
            if battery.total.import_ is None:
                battery.total.import_ = EnergyData()
            battery.total.import_.Wh = val * 1000
            
            
        # === METER SECTION ===
        
        # L1 phase
        l1_voltage = decode(37101)
        l1_current = decode(37107)
        l1_power = decode(37132)
        if l1_voltage is not None or l1_current is not None or l1_power is not None:
            meter.L1 = PhaseData()
            if l1_voltage is not None:
                meter.L1.V = l1_voltage
            if l1_current is not None:
                meter.L1.A = l1_current * -1
            if l1_power is not None:
                meter.L1.W = l1_power
        
        # L2 phase
        l2_voltage = decode(37103)
        l2_current = decode(37109)
        l2_power = decode(37134)
        if l2_voltage is not None or l2_current is not None or l2_power is not None:
            meter.L2 = PhaseData()
            if l2_voltage is not None:
                meter.L2.V = l2_voltage
            if l2_current is not None:
                meter.L2.A = l2_current * -1
            if l2_power is not None:
                meter.L2.W = l2_power
        
        # L3 phase
        l3_voltage = decode(37105)
        l3_current = decode(37111)
        l3_power = decode(37136)
        if l3_voltage is not None or l3_current is not None or l3_power is not None:
            meter.L3 = PhaseData()
            if l3_voltage is not None:
                meter.L3.V = l3_voltage
            if l3_current is not None:
                meter.L3.A = l3_current * -1
            if l3_power is not None:
                meter.L3.W = l3_power
            
            
        val = decode(37113)
        if val is not None:
            meter.W = val * -1
        
        val = decode(37118)
        if val is not None:
            meter.Hz = val
        
        val = decode(37119)
        if val is not None:
            if meter.total is None:
                meter.total = TotalEnergyData()
            if meter.total.import_ is None:
                meter.total.import_ = EnergyData()
            meter.total.import_.Wh = val * 1000
        
        val = decode(37121)
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
