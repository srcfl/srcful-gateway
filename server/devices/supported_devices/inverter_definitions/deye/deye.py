from ....profile_keys import (
    ProtocolKey,
    ProfileKey,
    RegistersKey,
    FunctionCodeKey,
    DeviceCategoryKey,
    DataTypeKey,
    EndiannessKey,
)
from ...profile import ModbusProfile
from ....common.types import ModbusDevice
from ....common.data_model import DERData, DERDataDefaults, RequiredKey, OptionalKey
from ....registerValue import RegisterValue
from .definitions_slim import deye_profile as slim_deye_profile


class DeyeProfile(ModbusProfile):
    def __init__(self):
        super().__init__(deye_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return True

    def get_decoded_data(self, raw_register_values: dict) -> DERData:
        """Decode raw register values into the DER data model using slim definitions, cleanly."""
        if not raw_register_values:
            return {}

        reg_defs = {entry[RegistersKey.START_REGISTER]: entry for entry in slim_deye_profile[ProfileKey.REGISTERS]}
        d = DERDataDefaults()
        out: DERData = {}

        # Map DERData keys to register(s) and any post-processing
        key_map = {
            RequiredKey.PV_POWER.value: [672, 673, 674, 675],
            RequiredKey.BATTERY_POWER.value: 590,
            RequiredKey.BATTERY_CURRENT.value: 591,
            RequiredKey.BATTERY_VOLTAGE.value: 587,
            RequiredKey.BATTERY_SOC.value: 588,
            RequiredKey.GRID_TOTAL_ACTIVE_POWER.value: 619,
            RequiredKey.GRID_FREQUENCY.value: 609,
            OptionalKey.RATED_POWER.value: 20,
            OptionalKey.MPPT1_VOLTAGE.value: 676,
            OptionalKey.MPPT1_CURRENT.value: 677,
            OptionalKey.MPPT2_VOLTAGE.value: 678,
            OptionalKey.MPPT2_CURRENT.value: 679,
            OptionalKey.INVERTER_TEMPERATURE.value: 541,
            OptionalKey.TOTAL_PV_GENERATION.value: 534,
            OptionalKey.BATTERY_TEMPERATURE.value: 217,
            OptionalKey.TOTAL_CHARGE_ENERGY.value: 516,
            OptionalKey.TOTAL_DISCHARGE_ENERGY.value: 518,
            OptionalKey.METER_L1_CURRENT.value: 610,
            OptionalKey.METER_L2_CURRENT.value: 611,
            OptionalKey.METER_L3_CURRENT.value: 612,
            OptionalKey.METER_L1_VOLTAGE.value: 598,
            OptionalKey.METER_L2_VOLTAGE.value: 599,
            OptionalKey.METER_L3_VOLTAGE.value: 600,
            OptionalKey.METER_ACTIVE_POWER_A.value: 616,
            OptionalKey.METER_ACTIVE_POWER_B.value: 617,
            OptionalKey.METER_ACTIVE_POWER_C.value: 618,
            OptionalKey.LOAD_POWER.value: 653,
            OptionalKey.TOTAL_IMPORT_ENERGY.value: 522,
            OptionalKey.TOTAL_EXPORT_ENERGY.value: 524,
        }

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
            rv = RegisterValue(
                address=addr,
                size=size,
                function_code=entry[RegistersKey.FUNCTION_CODE],
                data_type=entry[RegistersKey.DATA_TYPE],
                scale_factor=entry[RegistersKey.SCALE_FACTOR],
                endianness=entry[RegistersKey.ENDIANNESS],
            )
            _, value = rv._interpret_value(raw)
            return value

        for key, reg in key_map.items():
            if isinstance(reg, list):
                # PV power sum
                vals = [decode(a) for a in reg]
                val = sum(v for v in vals if isinstance(v, (int, float))) if any(vals) else None
            elif key == OptionalKey.BATTERY_TEMPERATURE.value:
                # Special case: Li-bat temp adjustment
                raw_val = decode(reg)
                val = (raw_val - 1000.0) / 10.0 if isinstance(raw_val, (int, float)) else None
            else:
                val = decode(reg)
            if val is not None:
                out[key] = d.make_value(key, val, source="deye")

        return out


deye_profile = {
    ProfileKey.NAME: "deye",
    ProfileKey.MAKER: "Deye",
    ProfileKey.VERSION: "V1.1b3",
    ProfileKey.VERBOSE_ALWAYS: False,
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
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 125,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        # {
        #     RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
        #     RegistersKey.START_REGISTER: 250,
        #     RegistersKey.NUM_OF_REGISTERS: 125,
        # },
        # {
        #     RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
        #     RegistersKey.START_REGISTER: 375,
        #     RegistersKey.NUM_OF_REGISTERS: 125,
        # },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 500,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        {
            RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
            RegistersKey.START_REGISTER: 625,
            RegistersKey.NUM_OF_REGISTERS: 125,
        },
        # {
        #     RegistersKey.FUNCTION_CODE: FunctionCodeKey.READ_HOLDING_REGISTERS,
        #     RegistersKey.START_REGISTER: 750,
        #     RegistersKey.NUM_OF_REGISTERS: 51,
        # },
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
