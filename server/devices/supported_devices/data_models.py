from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List


class Unit(str, Enum):
    W = "W"
    kW = "kW"
    V = "V"
    A = "A"
    Hz = "Hz"
    C = "°C"
    PERCENT = "%"
    kWh = "kWh"


class FieldNames(str, Enum):
    """Field name mappings for DER data values."""
    # PV fields
    PV_POWER = "pv_power"
    RATED_POWER = "rated_power"
    MPPT1_VOLTAGE = "mppt1_voltage"
    MPPT1_CURRENT = "mppt1_current"
    MPPT2_VOLTAGE = "mppt2_voltage"
    MPPT2_CURRENT = "mppt2_current"
    INVERTER_TEMPERATURE = "inverter_temperature"
    TOTAL_PV_GENERATION = "total_pv_generation"
    
    # Battery fields
    BATTERY_POWER = "battery_power"
    BATTERY_CURRENT = "battery_current"
    BATTERY_VOLTAGE = "battery_voltage"
    BATTERY_SOC = "battery_soc"
    HV_LV_SYSTEM = "hv_lv_system"
    BATTERY_TEMPERATURE = "battery_temperature"
    TOTAL_CHARGE_ENERGY = "total_charge_energy"
    TOTAL_DISCHARGE_ENERGY = "total_discharge_energy"

    # Meter fields
    ACTIVE_POWER = "active_power"
    FREQUENCY = "frequency"
    METER_L1_CURRENT = "meter_l1_current"
    METER_L2_CURRENT = "meter_l2_current"
    METER_L3_CURRENT = "meter_l3_current"
    METER_L1_VOLTAGE = "meter_l1_voltage"
    METER_L2_VOLTAGE = "meter_l2_voltage"
    METER_L3_VOLTAGE = "meter_l3_voltage"
    METER_L1_ACTIVE_POWER = "meter_l1_active_power"
    METER_L2_ACTIVE_POWER = "meter_l2_active_power"
    METER_L3_ACTIVE_POWER = "meter_l3_active_power"
    TOTAL_IMPORT_ENERGY = "total_import_energy"
    TOTAL_EXPORT_ENERGY = "total_export_energy"


@dataclass
class Value:
    """Represents a measurement value with unit and name."""
    value: float
    unit: Unit
    name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        return {
            "value": self.value,
            "unit": self.unit.value,
            "name": self.name
        }


@dataclass
class PVData:
    """Photovoltaic system data."""
    name: str = "PV"
    pv_power: Optional[Value] = None  # Always negative
    rated_power: Optional[Value] = None
    mppt1_voltage: Optional[Value] = None
    mppt1_current: Optional[Value] = None  # Always negative (generation current)
    mppt2_voltage: Optional[Value] = None
    mppt2_current: Optional[Value] = None  # Always negative (generation current)
    inverter_temperature: Optional[Value] = None
    total_pv_generation: Optional[Value] = None  # Always positive (cumulative generation)

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                if isinstance(field_value, Value):
                    if verbose:
                        result[field_name] = field_value.to_dict()
                    else:
                        result[field_name] = field_value.value
                else:
                    result[field_name] = field_value
        return result


@dataclass
class BatteryData:
    """Battery system data."""
    name: str = "Battery"
    battery_power: Optional[Value] = None  # Positive when charging, negative when discharging
    battery_current: Optional[Value] = None  # Positive when charging, negative when discharging
    battery_voltage: Optional[Value] = None
    battery_soc: Optional[Value] = None  # State of charge
    hv_lv_system: Optional[Value] = None  # High/Low voltage indicator
    battery_temperature: Optional[Value] = None
    total_charge_energy: Optional[Value] = None  # Always positive (cumulative charging)
    total_discharge_energy: Optional[Value] = None  # Always positive (cumulative discharging)

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                if isinstance(field_value, Value):
                    if verbose:
                        result[field_name] = field_value.to_dict()
                    else:
                        result[field_name] = field_value.value
                else:
                    result[field_name] = field_value
        return result


@dataclass
class MeterData:
    """Meter system data."""
    name: str = "meter"
    active_power: Optional[Value] = None  # Positive when importing, negative when exporting
    frequency: Optional[Value] = None
    meter_l1_current: Optional[Value] = None  # Positive when importing, negative when exporting
    meter_l2_current: Optional[Value] = None  # Positive when importing, negative when exporting
    meter_l3_current: Optional[Value] = None  # Positive when importing, negative when exporting
    meter_l1_voltage: Optional[Value] = None
    meter_l2_voltage: Optional[Value] = None
    meter_l3_voltage: Optional[Value] = None
    meter_l1_active_power: Optional[Value] = None  # Positive when importing, negative when exporting
    meter_l2_active_power: Optional[Value] = None  # Positive when importing, negative when exporting
    meter_l3_active_power: Optional[Value] = None  # Positive when importing, negative when exporting
    total_import_energy: Optional[Value] = None  # Always positive (cumulative import)
    total_export_energy: Optional[Value] = None  # Always positive (cumulative export)

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                if isinstance(field_value, Value):
                    if verbose:
                        result[field_name] = field_value.to_dict()
                    else:
                        result[field_name] = field_value.value
                else:
                    result[field_name] = field_value
        return result


@dataclass
class DERData:
    """Complete Distributed Energy Resource data model."""
    pv: Optional[PVData] = None
    battery: Optional[BatteryData] = None
    meter: Optional[MeterData] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        if self.pv is not None:
            result.update(self.pv.to_dict())
        if self.battery is not None:
            result.update(self.battery.to_dict())
        if self.meter is not None:
            result.update(self.meter.to_dict())
        return result
    
    def get_ders(self) -> List[PVData | BatteryData | MeterData]:
        return [der for der in [self.pv, self.battery, self.meter] if der is not None]

    def is_empty(self) -> bool:
        """Check if all data sections are empty."""
        return self.pv is None and self.battery is None and self.meter is None
