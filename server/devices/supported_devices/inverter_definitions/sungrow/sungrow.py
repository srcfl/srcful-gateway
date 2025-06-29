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
from server.devices.supported_devices.profile import RegisterInterval, WriteCommand
from .sungrow_legacy_profile import sungrow_legacy_profile


class SungrowProfile(ModbusProfile):

    DEVICE_TYPE_REGISTER = 4999
    RATED_POWER_REGISTER = 5000
    PV_STRING_POWER_REGISTER = 5016
    INVERTER_TEMPERATURE_REGISTER = 5007
    PV_TOTAL_ENERGY_REGISTER = 13002

    # Battery related registers
    BATTERY_POWER_REGISTER = 13021
    BATTERY_CURRENT_REGISTER = 13020
    BATTERY_VOLTAGE_REGISTER = 13019
    BATTERY_TEMPERATURE_REGISTER = 13024
    BATTERY_SOC_REGISTER = 13022
    BATTERY_CAPACITY_REGISTER = 13038
    BATTERY_TOTAL_CHARGE_ENERGY_REGISTER = 13040
    BATTERY_TOTAL_DISCHARGE_ENERGY_REGISTER = 13026

    # Grid related registers
    L1_CURRENT_REGISTER = 13030
    L2_CURRENT_REGISTER = 13031
    L3_CURRENT_REGISTER = 13032
    L1_VOLTAGE_REGISTER = 5018
    L2_VOLTAGE_REGISTER = 5019
    L3_VOLTAGE_REGISTER = 5020
    L1_POWER_REGISTER = 5602
    L2_POWER_REGISTER = 5604
    L3_POWER_REGISTER = 5606
    GRID_FREQUENCY_REGISTER = 5035
    TOTAL_IMPORT_ENERGY_REGISTER = 13036
    TOTAL_EXPORT_ENERGY_REGISTER = 13045

    # Load related registers
    LOAD_POWER_REGISTER = 13007

    def __init__(self):
        super().__init__(sungrow_legacy_profile)

    def profile_is_valid(self, device: ModbusDevice) -> bool:
        return True

    def _get_metadata(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval]) -> EMetadata:

        DEVICE_TYPE = self.get_register_interval(self.DEVICE_TYPE_REGISTER, decoded_registers)
        RATED_POWER = self.get_register_interval(self.RATED_POWER_REGISTER, decoded_registers)

        return EMetadata(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            model=DEVICE_TYPE.decoded_value,
            rated_power=RATED_POWER.decoded_value,
        )

    def _get_solar(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval]) -> ESolarType:

        PV_STRING_POWER = self.get_register_interval(self.PV_STRING_POWER_REGISTER, decoded_registers)
        INVERTER_TEMPERATURE = self.get_register_interval(self.INVERTER_TEMPERATURE_REGISTER, decoded_registers)
        PV_TOTAL_ENERGY = self.get_register_interval(self.PV_TOTAL_ENERGY_REGISTER, decoded_registers)

        return ESolarType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            power=EPower(value=PV_STRING_POWER.decoded_value),
            temperature=ETemperature(value=INVERTER_TEMPERATURE.decoded_value),
            total_pv_energy=EEnergy(value=PV_TOTAL_ENERGY.decoded_value),
        )

    def _get_battery(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval]) -> EBatteryType:

        BATT_POWER = self.get_register_interval(self.BATTERY_POWER_REGISTER, decoded_registers)
        BATTERY_CURRENT = self.get_register_interval(self.BATTERY_CURRENT_REGISTER, decoded_registers)
        BATTERY_VOLTAGE = self.get_register_interval(self.BATTERY_VOLTAGE_REGISTER, decoded_registers)
        BATT_TEMPERATURE = self.get_register_interval(self.BATTERY_TEMPERATURE_REGISTER, decoded_registers)
        BATTERY_SOC = self.get_register_interval(self.BATTERY_SOC_REGISTER, decoded_registers)
        BATTERY_CAPACITY = self.get_register_interval(self.BATTERY_CAPACITY_REGISTER, decoded_registers)
        BATT_TOTAL_CHARGE_ENERGY = self.get_register_interval(self.BATTERY_TOTAL_CHARGE_ENERGY_REGISTER, decoded_registers)
        BATT_TOTAL_DISCHARGE_ENERGY = self.get_register_interval(self.BATTERY_TOTAL_DISCHARGE_ENERGY_REGISTER, decoded_registers)

        return EBatteryType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            power=EPower(value=BATT_POWER.decoded_value),
            current=ECurrent(value=BATTERY_CURRENT.decoded_value),
            voltage=EVoltage(value=BATTERY_VOLTAGE.decoded_value),
            temperature=ETemperature(value=BATT_TEMPERATURE.decoded_value),
            soc=EPercent(value=BATTERY_SOC.decoded_value),
            capacity=EEnergy(value=BATTERY_CAPACITY.decoded_value),
            total_charge_energy=EEnergy(value=BATT_TOTAL_CHARGE_ENERGY.decoded_value),
            total_discharge_energy=EEnergy(value=BATT_TOTAL_DISCHARGE_ENERGY.decoded_value),
        )

    def _get_grid(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval]) -> EGridType:

        L1_CURRENT = self.get_register_interval(self.L1_CURRENT_REGISTER, decoded_registers)
        L2_CURRENT = self.get_register_interval(self.L2_CURRENT_REGISTER, decoded_registers)
        L3_CURRENT = self.get_register_interval(self.L3_CURRENT_REGISTER, decoded_registers)
        L1_VOLTAGE = self.get_register_interval(self.L1_VOLTAGE_REGISTER, decoded_registers)
        L2_VOLTAGE = self.get_register_interval(self.L2_VOLTAGE_REGISTER, decoded_registers)
        L3_VOLTAGE = self.get_register_interval(self.L3_VOLTAGE_REGISTER, decoded_registers)
        L1_POWER = self.get_register_interval(self.L1_POWER_REGISTER, decoded_registers)
        L2_POWER = self.get_register_interval(self.L2_POWER_REGISTER, decoded_registers)
        L3_POWER = self.get_register_interval(self.L3_POWER_REGISTER, decoded_registers)
        GRID_FREQUENCY = self.get_register_interval(self.GRID_FREQUENCY_REGISTER, decoded_registers)
        TOTAL_IMPORT_ENERGY = self.get_register_interval(self.TOTAL_IMPORT_ENERGY_REGISTER, decoded_registers)
        TOTAL_EXPORT_ENERGY = self.get_register_interval(self.TOTAL_EXPORT_ENERGY_REGISTER, decoded_registers)

        return EGridType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            l1_A=ECurrent(value=L1_CURRENT.decoded_value),
            l2_A=ECurrent(value=L2_CURRENT.decoded_value),
            l3_A=ECurrent(value=L3_CURRENT.decoded_value),
            l1_V=EVoltage(value=L1_VOLTAGE.decoded_value),
            l2_V=EVoltage(value=L2_VOLTAGE.decoded_value),
            l3_V=EVoltage(value=L3_VOLTAGE.decoded_value),
            l1_W=EPower(value=L1_POWER.decoded_value),
            l2_W=EPower(value=L2_POWER.decoded_value),
            l3_W=EPower(value=L3_POWER.decoded_value),
            grid_frequency=EFrequency(value=GRID_FREQUENCY.decoded_value),
            total_import_energy=EEnergy(value=TOTAL_IMPORT_ENERGY.decoded_value),
            total_export_energy=EEnergy(value=TOTAL_EXPORT_ENERGY.decoded_value),
        )

    def _get_load(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval]) -> ELoadType:
        LOAD_P = self.get_register_interval(self.LOAD_POWER_REGISTER, decoded_registers)
        return ELoadType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            power=EPower(value=LOAD_P.decoded_value),
        )

    def _get_esystem_data(self, device_sn: str, timestamp_ms: int, harvest: dict) -> List[EBaseType]:

        decoded_registers = self.get_decoded_registers(harvest)

        esystem_data: List[EBaseType] = []

        # Collect potential EType data objects
        potential_data = [
            self._get_metadata(device_sn, timestamp_ms, decoded_registers),
            self._get_grid(device_sn, timestamp_ms, decoded_registers),
            self._get_battery(device_sn, timestamp_ms, decoded_registers),
            self._get_solar(device_sn, timestamp_ms, decoded_registers),
            self._get_load(device_sn, timestamp_ms, decoded_registers),
        ]

        # Append only the objects that were successfully created (i.e., not None)
        esystem_data.extend([data for data in potential_data if data is not None])

        return esystem_data

    def _get_init_commands(self) -> List[WriteCommand]:
        return []

    def _generate_charge_commands(self, type: EBatteryType) -> List[WriteCommand]:
        return []

    def _generate_discharge_commands(self, type: EBatteryType) -> List[WriteCommand]:
        return []

    def get_write_commands(self, esystem_data: List[EBaseType]) -> List[WriteCommand]:
        return []
