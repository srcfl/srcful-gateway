from ....profile_keys import (
    ProtocolKey,
    ProfileKey,
    RegistersKey,
    FunctionCodeKey,
    DataTypeKey,
    EndiannessKey,
)
from server.e_system.types import (
    EBaseType,
    EMetadata,
    EGridType,
    EBatteryType,
    ESolarType,
    ELoadType,
    ECurrent,
    EVoltage,
    EPower,
    ETemperature,
    EPercent,
    EFrequency,
    EEnergy,
)
from ...profile import ModbusProfile
from ....common.types import ModbusDevice
from typing import List
from server.devices.supported_devices.profile import RegisterInterval
from .deye_register_definitions import deye_registers


class DeyeProfile(ModbusProfile):
    def __init__(self):
        super().__init__(deye_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return True

    def get_register_interval(self, register: int, register_intervals: List[RegisterInterval]) -> RegisterInterval:
        for register_interval in register_intervals:
            if register_interval.start_register == register:
                return register_interval
        return None

    def _get_esystem_data(self, device_sn: str, timestamp_ms: int, harvest: dict) -> List[EBaseType]:

        decoded_registers = self.get_decoded_registers(harvest)

        esystem_data: List[EBaseType] = []

        # ------------------------------------------------------------
        # --- Metadata ---
        # ------------------------------------------------------------

        MODEL = "N/A"
        RATED_POWER = self.get_register_interval(20, decoded_registers)

        metadata_type = EMetadata(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            model=MODEL,
            rated_power=RATED_POWER.decoded_value,
        )

        # ------------------------------------------------------------
        # --- General ---
        # ------------------------------------------------------------

        HV_LV = self.get_register_interval(0, decoded_registers)
        hv_lv_power_sf = 10 if HV_LV.decoded_value == 6 else 1
        hv_lv_voltage_sf = 0.1 if HV_LV.decoded_value == 6 else 0.01

        # ------------------------------------------------------------
        # --- Solar ---
        # ------------------------------------------------------------

        PV_STRING_1 = self.get_register_interval(672, decoded_registers)
        PV_STRING_2 = self.get_register_interval(673, decoded_registers)
        PV_STRING_3 = self.get_register_interval(674, decoded_registers)
        PV_STRING_4 = self.get_register_interval(675, decoded_registers)
        pv_string_total_power = (PV_STRING_1.decoded_value + PV_STRING_2.decoded_value + PV_STRING_3.decoded_value + PV_STRING_4.decoded_value) * hv_lv_power_sf

        INVERTER_TEMPERATURE = self.get_register_interval(541, decoded_registers)

        PV_TOTAL_ENERGY = self.get_register_interval(534, decoded_registers)

        solar_type = ESolarType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            POWER=EPower(value=pv_string_total_power),
            TEMPERATURE=ETemperature(value=INVERTER_TEMPERATURE.decoded_value),
            TOTAL_PV_ENERGY=EEnergy(value=PV_TOTAL_ENERGY.decoded_value),
        )

        # ------------------------------------------------------------
        # --- Battery ---
        # ------------------------------------------------------------

        BATT_POWER = self.get_register_interval(590, decoded_registers)
        BATTERY_CURRENT = self.get_register_interval(591, decoded_registers)
        BATTERY_VOLTAGE = self.get_register_interval(587, decoded_registers)
        BATT_TEMPERATURE = self.get_register_interval(217, decoded_registers)
        BATT_TEMPERATURE.decoded_value = BATT_TEMPERATURE.decoded_value - 100
        BATTERY_SOC = self.get_register_interval(588, decoded_registers)
        BATTERY_CAPACITY = self.get_register_interval(102, decoded_registers)
        BATTERY_CAPACITY.decoded_value *= BATTERY_VOLTAGE.decoded_value * hv_lv_voltage_sf  # Convert Ah to Wh
        BATT_TOTAL_CHARGE_ENERGY = self.get_register_interval(516, decoded_registers)
        BATT_TOTAL_DISCHARGE_ENERGY = self.get_register_interval(518, decoded_registers)

        battery_type = EBatteryType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            POWER=EPower(value=BATT_POWER.decoded_value * hv_lv_power_sf),
            CURRENT=ECurrent(value=BATTERY_CURRENT.decoded_value),
            VOLTAGE=EVoltage(value=BATTERY_VOLTAGE.decoded_value * hv_lv_voltage_sf),
            SOC=EPercent(value=BATTERY_SOC.decoded_value),
            CAPACITY=EEnergy(value=BATTERY_CAPACITY.decoded_value),
            TEMPERATURE=ETemperature(value=BATT_TEMPERATURE.decoded_value),
            TOTAL_CHARGE_ENERGY=EEnergy(value=BATT_TOTAL_CHARGE_ENERGY.decoded_value),
            TOTAL_DISCHARGE_ENERGY=EEnergy(value=BATT_TOTAL_DISCHARGE_ENERGY.decoded_value),
        )

        # ------------------------------------------------------------
        # --- Meter ---
        # ------------------------------------------------------------

        L1_CURRENT = self.get_register_interval(610, decoded_registers)
        L2_CURRENT = self.get_register_interval(611, decoded_registers)
        L3_CURRENT = self.get_register_interval(612, decoded_registers)
        L1_VOLTAGE = self.get_register_interval(598, decoded_registers)
        L2_VOLTAGE = self.get_register_interval(599, decoded_registers)
        L3_VOLTAGE = self.get_register_interval(600, decoded_registers)
        L1_POWER = self.get_register_interval(622, decoded_registers)
        L2_POWER = self.get_register_interval(623, decoded_registers)
        L3_POWER = self.get_register_interval(624, decoded_registers)
        GRID_FREQUENCY = self.get_register_interval(609, decoded_registers)
        TOTAL_IMPORT_ENERGY = self.get_register_interval(522, decoded_registers)
        TOTAL_EXPORT_ENERGY = self.get_register_interval(524, decoded_registers)

        grid_type = EGridType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            L1_A=ECurrent(value=L1_CURRENT.decoded_value),
            L2_A=ECurrent(value=L2_CURRENT.decoded_value),
            L3_A=ECurrent(value=L3_CURRENT.decoded_value),
            L1_V=EVoltage(value=L1_VOLTAGE.decoded_value),
            L2_V=EVoltage(value=L2_VOLTAGE.decoded_value),
            L3_V=EVoltage(value=L3_VOLTAGE.decoded_value),
            L1_P=EPower(value=L1_POWER.decoded_value),
            L2_P=EPower(value=L2_POWER.decoded_value),
            L3_P=EPower(value=L3_POWER.decoded_value),
            GRID_FREQUENCY=EFrequency(value=GRID_FREQUENCY.decoded_value),
            TOTAL_IMPORT_ENERGY=EEnergy(value=TOTAL_IMPORT_ENERGY.decoded_value),
            TOTAL_EXPORT_ENERGY=EEnergy(value=TOTAL_EXPORT_ENERGY.decoded_value),
        )

        # ------------------------------------------------------------
        # --- Household Load ---
        # ------------------------------------------------------------

        LOAD_P = self.get_register_interval(653, decoded_registers)  # TODO: Incorrect, fix later

        load_type = ELoadType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            POWER=EPower(value=LOAD_P.decoded_value),
        )

        esystem_data.append(metadata_type)
        esystem_data.append(grid_type)
        esystem_data.append(battery_type)
        esystem_data.append(solar_type)
        esystem_data.append(load_type)

        return esystem_data


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
    ProfileKey.ALL_REGISTERS: deye_registers,
    ProfileKey.KEYWORDS: ["deye", "high-flying"],
}
