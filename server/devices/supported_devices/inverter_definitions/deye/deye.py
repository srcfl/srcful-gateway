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
from .deye_legacy_profile import deye_legacy_profile


class DeyeProfile(ModbusProfile):

    # PV related registers
    PV_STRING_1_REGISTER = 672
    PV_STRING_2_REGISTER = 673
    PV_STRING_3_REGISTER = 674
    PV_STRING_4_REGISTER = 675
    INVERTER_TEMPERATURE_REGISTER = 541
    PV_TOTAL_ENERGY_REGISTER = 534
    PV_POWER_SELL_TO_GRID_REGISTER = 145

    # Battery related registers
    BATTERY_POWER_REGISTER = 590
    BATTERY_CURRENT_REGISTER = 591
    BATTERY_VOLTAGE_REGISTER = 587
    BATTERY_TEMPERATURE_REGISTER = 217
    BATTERY_SOC_REGISTER = 588
    BATTERY_CAPACITY_REGISTER = 102
    BATTERY_TOTAL_CHARGE_ENERGY_REGISTER = 516
    BATTERY_TOTAL_DISCHARGE_ENERGY_REGISTER = 518

    # Grid related registers
    L1_CURRENT_REGISTER = 610
    L2_CURRENT_REGISTER = 611
    L3_CURRENT_REGISTER = 612
    L1_VOLTAGE_REGISTER = 598
    L2_VOLTAGE_REGISTER = 599
    L3_VOLTAGE_REGISTER = 600
    L1_POWER_REGISTER = 622
    L2_POWER_REGISTER = 623
    L3_POWER_REGISTER = 624
    GRID_FREQUENCY_REGISTER = 609
    TOTAL_IMPORT_ENERGY_REGISTER = 522
    TOTAL_EXPORT_ENERGY_REGISTER = 524

    # Control registers
    BATTERY_LIMIT_CONTROL_REGISTER = 142
    TOU_ENABLE_CONTROL_REGISTER = 146
    TOU_START_TIME_REGISTER = 148
    TOU_END_TIME_REGISTER = 149
    BATTERY_OUTPUT_POWER_REGISTER = 154
    BATTERY_TARGET_SOC_REGISTER = 166
    BATTERY_MAX_CHARGE_CURRENT_REGISTER = 108
    BATTERY_MAX_DISCHARGE_CURRENT_REGISTER = 109
    BATTERY_CHARGE_CURRENT_REGISTER = 128
    GENERATOR_CHARGE_ENABLE_REGISTER = 129
    UTILITY_CHARGE_ENABLE_REGISTER = 130
    ENERGY_MANAGEMENT_ENABLE_REGISTER = 141
    LIMIT_CONTROL_REGISTER = 142
    MAX_SELL_TO_GRID_POWER_REGISTER = 143
    BATTERY_ENABLE_CHARGE_REGISTER = 172
    CONTROL_BOARD_SPECIAL_FUNCTION_REGISTER = 178

    # Configurations, these should come from the backend, not be hard-coded here
    BATTERY_MAX_CHARGE_POWER = 5000  # W
    BATTERY_MAX_DISCHARGE_POWER = 5000  # W
    BATTERY_TARGET_SOC_MAX = 90
    BATTERY_TARGET_SOC_MIN = 10
    CONTROL_BOARD_SPECIAL_FUNCTION_DEFAULT = 11946  # everything disabled except "Lost Lithium Battery Fault"
    BATTERY_MAX_CHARGE_CURRENT_DEFAULT = 31  # A
    BATTERY_MAX_DISCHARGE_CURRENT_DEFAULT = 31  # A
    BATTERY_CHARGE_CURRENT_DEFAULT = 31  # A
    GENERATOR_CHARGE_ENABLE_DEFAULT = 1
    UTILITY_CHARGE_ENABLE_DEFAULT = 1
    ENERGY_MANAGEMENT_ENABLE_DEFAULT = 3  # Load first
    LIMIT_CONTROL_DEFAULT = 2  # Self-consumption mode
    MAX_SELL_TO_GRID_POWER_DEFAULT = 10000  # W
    PV_SELL_TO_GRID_DEFAULT = 1
    TOU_ENABLE_DEFAULT = 1
    TOU_START_TIME_DEFAULT = 0  # 00:00
    TOU_END_TIME_DEFAULT = 2355  # 23:55

    def __init__(self):
        super().__init__(deye_legacy_profile)
        self.hv_lv_power_sf = None
        self.hv_lv_voltage_sf = None

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
        PV_STRING_1 = self.get_register_interval(self.PV_STRING_1_REGISTER, decoded_registers)
        PV_STRING_2 = self.get_register_interval(self.PV_STRING_2_REGISTER, decoded_registers)
        PV_STRING_3 = self.get_register_interval(self.PV_STRING_3_REGISTER, decoded_registers)
        PV_STRING_4 = self.get_register_interval(self.PV_STRING_4_REGISTER, decoded_registers)
        pv_string_total_power = (PV_STRING_1.decoded_value + PV_STRING_2.decoded_value + PV_STRING_3.decoded_value + PV_STRING_4.decoded_value) * hv_lv_power_sf

        INVERTER_TEMPERATURE = self.get_register_interval(self.INVERTER_TEMPERATURE_REGISTER, decoded_registers)

        PV_TOTAL_ENERGY = self.get_register_interval(self.PV_TOTAL_ENERGY_REGISTER, decoded_registers)

        return ESolarType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            power=EPower(value=pv_string_total_power),
            temperature=ETemperature(value=INVERTER_TEMPERATURE.decoded_value),
            total_pv_energy=EEnergy(value=PV_TOTAL_ENERGY.decoded_value),
        )

    def _get_battery(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval], hv_lv_power_sf: float, hv_lv_voltage_sf: float) -> Optional[EBatteryType]:
        BATT_POWER = self.get_register_interval(self.BATTERY_POWER_REGISTER, decoded_registers)
        BATTERY_CURRENT = self.get_register_interval(self.BATTERY_CURRENT_REGISTER, decoded_registers)
        BATTERY_VOLTAGE = self.get_register_interval(self.BATTERY_VOLTAGE_REGISTER, decoded_registers)
        BATT_TEMPERATURE = self.get_register_interval(self.BATTERY_TEMPERATURE_REGISTER, decoded_registers)
        BATT_TEMPERATURE.decoded_value = BATT_TEMPERATURE.decoded_value - 100
        BATTERY_SOC = self.get_register_interval(self.BATTERY_SOC_REGISTER, decoded_registers)
        BATTERY_CAPACITY = self.get_register_interval(self.BATTERY_CAPACITY_REGISTER, decoded_registers)
        BATTERY_CAPACITY.decoded_value *= BATTERY_VOLTAGE.decoded_value * hv_lv_voltage_sf  # Convert Ah to Wh
        BATT_TOTAL_CHARGE_ENERGY = self.get_register_interval(self.BATTERY_TOTAL_CHARGE_ENERGY_REGISTER, decoded_registers)
        BATT_TOTAL_DISCHARGE_ENERGY = self.get_register_interval(self.BATTERY_TOTAL_DISCHARGE_ENERGY_REGISTER, decoded_registers)

        if BATTERY_SOC.decoded_value and 0 < BATTERY_SOC.decoded_value <= 100:
            return EBatteryType(
                device_sn=device_sn,
                timestamp_ms=timestamp_ms,
                power=EPower(value=BATT_POWER.decoded_value * hv_lv_power_sf),
                current=ECurrent(value=BATTERY_CURRENT.decoded_value),
                voltage=EVoltage(value=BATTERY_VOLTAGE.decoded_value * hv_lv_voltage_sf),
                soc=EPercent(value=BATTERY_SOC.decoded_value),
                capacity=EEnergy(value=BATTERY_CAPACITY.decoded_value),
                temperature=ETemperature(value=BATT_TEMPERATURE.decoded_value),
                total_charge_energy=EEnergy(value=BATT_TOTAL_CHARGE_ENERGY.decoded_value),
                total_discharge_energy=EEnergy(value=BATT_TOTAL_DISCHARGE_ENERGY.decoded_value),
            )
        else:
            return None

    def _get_grid(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval]) -> Optional[EGridType]:
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

        if TOTAL_IMPORT_ENERGY.decoded_value > 0:
            return EGridType(
                device_sn=device_sn,
                timestamp_ms=timestamp_ms,
                l1_A=ECurrent(value=L1_CURRENT.decoded_value),
                l2_A=ECurrent(value=L2_CURRENT.decoded_value),
                l3_A=ECurrent(value=L3_CURRENT.decoded_value),
                l1_V=EVoltage(value=L1_VOLTAGE.decoded_value),
                l2_V=EVoltage(value=L2_VOLTAGE.decoded_value),
                l3_V=EVoltage(value=L3_VOLTAGE.decoded_value),
                l1_P=EPower(value=L1_POWER.decoded_value),
                l2_P=EPower(value=L2_POWER.decoded_value),
                l3_P=EPower(value=L3_POWER.decoded_value),
                grid_frequency=EFrequency(value=GRID_FREQUENCY.decoded_value),
                total_import_energy=EEnergy(value=TOTAL_IMPORT_ENERGY.decoded_value),
                total_export_energy=EEnergy(value=TOTAL_EXPORT_ENERGY.decoded_value),
            )
        else:
            return None

    def _get_load(self, device_sn: str, timestamp_ms: int, decoded_registers: List[RegisterInterval]) -> ELoadType:
        LOAD_P = self.get_register_interval(653, decoded_registers)
        return ELoadType(
            device_sn=device_sn,
            timestamp_ms=timestamp_ms,
            power=EPower(value=LOAD_P.decoded_value),
        )

    def _get_esystem_data(self, device_sn: str, timestamp_ms: int, harvest: dict) -> List[EBaseType]:

        decoded_registers = self.get_decoded_registers(harvest)

        esystem_data: List[EBaseType] = []

        # Deye specific scaling factors, depending on if the system is high voltage or low voltage
        HV_LV = self.get_register_interval(0, decoded_registers)
        self.hv_lv_power_sf = 10 if HV_LV.decoded_value == 6 else 1
        self.hv_lv_voltage_sf = 0.1 if HV_LV.decoded_value == 6 else 0.01

        # Collect potential EType data objects
        potential_data = [
            self._get_metadata(device_sn, timestamp_ms, decoded_registers),
            self._get_grid(device_sn, timestamp_ms, decoded_registers),
            self._get_battery(device_sn, timestamp_ms, decoded_registers, self.hv_lv_power_sf, self.hv_lv_voltage_sf),
            self._get_solar(device_sn, timestamp_ms, decoded_registers, self.hv_lv_power_sf),
            self._get_load(device_sn, timestamp_ms, decoded_registers),
        ]

        # Append only the objects that were successfully created (i.e., not None)
        esystem_data.extend([data for data in potential_data if data is not None])

        return esystem_data

    def _get_init_commands(self) -> List[WriteCommand]:
        commands: List[WriteCommand] = []

        commands.append(WriteCommand(self.CONTROL_BOARD_SPECIAL_FUNCTION_REGISTER, self.CONTROL_BOARD_SPECIAL_FUNCTION_DEFAULT))
        commands.append(WriteCommand(self.BATTERY_MAX_CHARGE_CURRENT_REGISTER, self.BATTERY_MAX_CHARGE_CURRENT_DEFAULT))
        commands.append(WriteCommand(self.BATTERY_MAX_DISCHARGE_CURRENT_REGISTER, self.BATTERY_MAX_DISCHARGE_CURRENT_DEFAULT))
        commands.append(WriteCommand(self.BATTERY_CHARGE_CURRENT_REGISTER, self.BATTERY_CHARGE_CURRENT_DEFAULT))
        commands.append(WriteCommand(self.GENERATOR_CHARGE_ENABLE_REGISTER, self.GENERATOR_CHARGE_ENABLE_DEFAULT))
        commands.append(WriteCommand(self.UTILITY_CHARGE_ENABLE_REGISTER, self.UTILITY_CHARGE_ENABLE_DEFAULT))
        commands.append(WriteCommand(self.ENERGY_MANAGEMENT_ENABLE_REGISTER, self.ENERGY_MANAGEMENT_ENABLE_DEFAULT))
        commands.append(WriteCommand(self.LIMIT_CONTROL_REGISTER, self.LIMIT_CONTROL_DEFAULT))
        commands.append(WriteCommand(self.MAX_SELL_TO_GRID_POWER_REGISTER, self.MAX_SELL_TO_GRID_POWER_DEFAULT // self.hv_lv_power_sf))
        commands.append(WriteCommand(self.PV_POWER_SELL_TO_GRID_REGISTER, self.PV_SELL_TO_GRID_DEFAULT))
        commands.append(WriteCommand(self.TOU_ENABLE_CONTROL_REGISTER, self.TOU_ENABLE_DEFAULT))
        commands.append(WriteCommand(self.TOU_START_TIME_REGISTER, self.TOU_START_TIME_DEFAULT))
        commands.append(WriteCommand(self.TOU_END_TIME_REGISTER, self.TOU_END_TIME_DEFAULT))

        return commands

    def _generate_charge_commands(self, type: EBatteryType) -> List[WriteCommand]:
        commands: List[WriteCommand] = []

        charge_current = type.power.value / type.voltage.value

        commands.append(WriteCommand(self.BATTERY_TARGET_SOC_REGISTER, self.BATTERY_TARGET_SOC_MAX))
        commands.append(WriteCommand(self.BATTERY_MAX_CHARGE_CURRENT_REGISTER, charge_current))
        commands.append(WriteCommand(self.BATTERY_ENABLE_CHARGE_REGISTER, 3))  # 1 is grid charge, 2 is battery charge, 3 is both
        return commands

    def _generate_discharge_commands(self, type: EBatteryType) -> List[WriteCommand]:
        commands: List[WriteCommand] = []

        power = type.power.value * self.hv_lv_power_sf

        commands.append(WriteCommand(self.BATTERY_OUTPUT_POWER_REGISTER, power))
        commands.append(WriteCommand(self.BATTERY_TARGET_SOC_REGISTER, self.BATTERY_TARGET_SOC_MIN))
        commands.append(WriteCommand(self.BATTERY_LIMIT_CONTROL_REGISTER, 0))  # 0 is Sell-to-grid enable, 1 is supply to backup load, 2 is self-consumption (with sell excess to grid)
        return commands

    def get_write_commands(self, esystem_data: List[EBaseType]) -> List[WriteCommand]:
        commands: List[WriteCommand] = []

        for type in esystem_data:
            if isinstance(type, EBatteryType):
                if type.power.value < 0:
                    commands.extend(self._generate_discharge_commands(type))
                elif type.power.value > 0:
                    commands.extend(self._generate_charge_commands(type))
                else:
                    pass  # No power, no action

        return commands
