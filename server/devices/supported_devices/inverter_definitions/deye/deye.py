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
from typing import List, Optional
from server.devices.supported_devices.profile import RegisterInterval
from .deye_legacy_profile import deye_legacy_profile


class DeyeProfile(ModbusProfile):
    def __init__(self):
        super().__init__(deye_legacy_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return True

    def _get_metadata(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval]) -> EMetadata:
        MODEL = "N/A"
        RATED_POWER = self.get_register_interval(20, decoded_registers)
        return EMetadata(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            model=MODEL,
            rated_power=RATED_POWER.decoded_value,
        )

    def _get_solar(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval], hv_lv_power_sf: float) -> ESolarType:
        PV_STRING_1 = self.get_register_interval(672, decoded_registers)
        PV_STRING_2 = self.get_register_interval(673, decoded_registers)
        PV_STRING_3 = self.get_register_interval(674, decoded_registers)
        PV_STRING_4 = self.get_register_interval(675, decoded_registers)
        pv_string_total_power = (PV_STRING_1.decoded_value + PV_STRING_2.decoded_value + PV_STRING_3.decoded_value + PV_STRING_4.decoded_value) * hv_lv_power_sf

        INVERTER_TEMPERATURE = self.get_register_interval(541, decoded_registers)

        PV_TOTAL_ENERGY = self.get_register_interval(534, decoded_registers)

        return ESolarType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            POWER=EPower(value=pv_string_total_power),
            TEMPERATURE=ETemperature(value=INVERTER_TEMPERATURE.decoded_value),
            TOTAL_PV_ENERGY=EEnergy(value=PV_TOTAL_ENERGY.decoded_value),
        )

    def _get_battery(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval], hv_lv_power_sf: float, hv_lv_voltage_sf: float) -> Optional[EBatteryType]:
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

        if BATTERY_SOC.decoded_value and 0 < BATTERY_SOC.decoded_value <= 100:
            return EBatteryType(
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
        else:
            return None

    def _get_grid(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval]) -> Optional[EGridType]:
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

        if TOTAL_IMPORT_ENERGY.decoded_value > 0:
            return EGridType(
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
        else:
            return None

    def _get_load(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval]) -> ELoadType:
        LOAD_P = self.get_register_interval(653, decoded_registers)
        return ELoadType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            POWER=EPower(value=LOAD_P.decoded_value),
        )

    def _get_esystem_data(self, device_sn: str, timestamp_ms: int, harvest: dict) -> List[EBaseType]:

        decoded_registers = self.get_decoded_registers(harvest)

        esystem_data: List[EBaseType] = []

        # Deye specific scaling factors, depending on if the system is high voltage or low voltage
        HV_LV = self.get_register_interval(0, decoded_registers)
        hv_lv_power_sf = 10 if HV_LV.decoded_value == 6 else 1
        hv_lv_voltage_sf = 0.1 if HV_LV.decoded_value == 6 else 0.01

        # Collect potential EType data objects
        potential_data = [
            self._get_metadata(device_sn, timestamp_ms, decoded_registers),
            self._get_grid(device_sn, timestamp_ms, decoded_registers),
            self._get_battery(device_sn, timestamp_ms, decoded_registers, hv_lv_power_sf, hv_lv_voltage_sf),
            self._get_solar(device_sn, timestamp_ms, decoded_registers, hv_lv_power_sf),
            self._get_load(device_sn, timestamp_ms, decoded_registers),
        ]

        # Append only the objects that were successfully created (i.e., not None)
        esystem_data.extend([data for data in potential_data if data is not None])

        return esystem_data
