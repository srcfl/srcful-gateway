from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, TypedDict, Literal


class Unit(str, Enum):
	W = "W"
	kW = "kW"
	V = "V"
	A = "A"
	Hz = "Hz"
	C = "°C"
	PERCENT = "%"
	kWh = "kWh"


class RequiredKey(str, Enum):
	PV_POWER = "pv_power"
	BATTERY_POWER = "battery_power"
	BATTERY_CURRENT = "battery_current"
	BATTERY_VOLTAGE = "battery_voltage"
	BATTERY_SOC = "battery_soc"
	GRID_TOTAL_ACTIVE_POWER = "grid_total_active_power"
	GRID_FREQUENCY = "grid_frequency"


class OptionalKey(str, Enum):
	# General
	RATED_POWER = "rated_power"
	# PV related
	MPPT1_VOLTAGE = "mppt1_voltage"
	MPPT1_CURRENT = "mppt1_current"
	MPPT2_VOLTAGE = "mppt2_voltage"
	MPPT2_CURRENT = "mppt2_current"
	INVERTER_TEMPERATURE = "inverter_temperature"
	TOTAL_PV_GENERATION = "total_pv_generation"
	# Battery related
	HV_LV_SYSTEM = "hv_lv_system"
	BATTERY_TEMPERATURE = "battery_temperature"
	TOTAL_CHARGE_ENERGY = "total_charge_energy"
	TOTAL_DISCHARGE_ENERGY = "total_discharge_energy"
	# Grid related
	METER_L1_CURRENT = "meter_l1_current"
	METER_L2_CURRENT = "meter_l2_current"
	METER_L3_CURRENT = "meter_l3_current"
	METER_L1_VOLTAGE = "meter_l1_voltage"
	METER_L2_VOLTAGE = "meter_l2_voltage"
	METER_L3_VOLTAGE = "meter_l3_voltage"
	METER_ACTIVE_POWER_A = "meter_active_power_a"
	METER_ACTIVE_POWER_B = "meter_active_power_b"
	METER_ACTIVE_POWER_C = "meter_active_power_c"
	LOAD_POWER = "load_power"
	TOTAL_IMPORT_ENERGY = "total_import_energy"
	TOTAL_EXPORT_ENERGY = "total_export_energy"


class Value(TypedDict, total=False):
	value: float
	unit: str
	source: Optional[str]


class DERData(TypedDict, total=False):
	# Required for schedule generation (may still be absent temporarily)
	pv_power: Value
	battery_power: Value
	battery_current: Value
	battery_voltage: Value
	battery_soc: Value
	grid_total_active_power: Value
	grid_frequency: Value

	# Optional
	rated_power: Value
	mppt1_voltage: Value
	mppt1_current: Value
	mppt2_voltage: Value
	mppt2_current: Value
	inverter_temperature: Value
	total_pv_generation: Value
	hv_lv_system: Value
	battery_temperature: Value
	total_charge_energy: Value
	total_discharge_energy: Value
	meter_l1_current: Value
	meter_l2_current: Value
	meter_l3_current: Value
	meter_l1_voltage: Value
	meter_l2_voltage: Value
	meter_l3_voltage: Value
	meter_active_power_a: Value
	meter_active_power_b: Value
	meter_active_power_c: Value
	load_power: Value
	total_import_energy: Value
	total_export_energy: Value


@dataclass
class DERDataDefaults:
	"""Helper to provide units for each canonical key."""
	units: Dict[str, Unit] = field(default_factory=lambda: {
		# Required
		RequiredKey.PV_POWER.value: Unit.W,
		RequiredKey.BATTERY_POWER.value: Unit.W,
		RequiredKey.BATTERY_CURRENT.value: Unit.A,
		RequiredKey.BATTERY_VOLTAGE.value: Unit.V,
		RequiredKey.BATTERY_SOC.value: Unit.PERCENT,
		RequiredKey.GRID_TOTAL_ACTIVE_POWER.value: Unit.W,
		RequiredKey.GRID_FREQUENCY.value: Unit.Hz,
		# Optional
		OptionalKey.RATED_POWER.value: Unit.W,
		OptionalKey.MPPT1_VOLTAGE.value: Unit.V,
		OptionalKey.MPPT1_CURRENT.value: Unit.A,
		OptionalKey.MPPT2_VOLTAGE.value: Unit.V,
		OptionalKey.MPPT2_CURRENT.value: Unit.A,
		OptionalKey.INVERTER_TEMPERATURE.value: Unit.C,
		OptionalKey.TOTAL_PV_GENERATION.value: Unit.kWh,
		OptionalKey.HV_LV_SYSTEM.value: Unit.W,  # dimensionless, but keep numeric; could switch to None
		OptionalKey.BATTERY_TEMPERATURE.value: Unit.C,
		OptionalKey.TOTAL_CHARGE_ENERGY.value: Unit.kWh,
		OptionalKey.TOTAL_DISCHARGE_ENERGY.value: Unit.kWh,
		OptionalKey.METER_L1_CURRENT.value: Unit.A,
		OptionalKey.METER_L2_CURRENT.value: Unit.A,
		OptionalKey.METER_L3_CURRENT.value: Unit.A,
		OptionalKey.METER_L1_VOLTAGE.value: Unit.V,
		OptionalKey.METER_L2_VOLTAGE.value: Unit.V,
		OptionalKey.METER_L3_VOLTAGE.value: Unit.V,
		OptionalKey.METER_ACTIVE_POWER_A.value: Unit.W,
		OptionalKey.METER_ACTIVE_POWER_B.value: Unit.W,
		OptionalKey.METER_ACTIVE_POWER_C.value: Unit.W,
		OptionalKey.LOAD_POWER.value: Unit.W,
		OptionalKey.TOTAL_IMPORT_ENERGY.value: Unit.kWh,
		OptionalKey.TOTAL_EXPORT_ENERGY.value: Unit.kWh,
	})

	def make_value(self, key: str, value: float, source: Optional[str] = None) -> Value:
		unit = self.units.get(key)
		return {"value": float(value), "unit": unit.value if unit else "", "source": source}


# Lightweight contract for decoders
DecodedInput = Dict[int | str, int | float | str | bytes]


def new_empty_der_data() -> DERData:
	"""Convenience factory for an empty DER data dict."""
	return {}
