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
    Wh = "Wh"


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
class MPPTData:
    """MPPT (Maximum Power Point Tracker) data."""
    voltage: Optional[Value] = None
    current: Optional[Value] = None  # Always negative (generation current)

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

    def is_empty(self) -> bool:
        """Check if this MPPT has any data."""
        return self.voltage is None and self.current is None


@dataclass
class PhaseData:
    """Single phase electrical measurements."""
    voltage: Optional[Value] = None
    current: Optional[Value] = None  # Positive when importing, negative when exporting
    active_power: Optional[Value] = None  # Positive when importing, negative when exporting

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

    def is_empty(self) -> bool:
        """Check if this phase has any data."""
        return self.voltage is None and self.current is None and self.active_power is None


@dataclass
class PVData:
    """Photovoltaic system data."""
    name: str = "PV"
    power: Optional[Value] = None  # Always negative
    rated_power: Optional[Value] = None
    hv_lv_system: Optional[Value] = None  # High/Low voltage indicator
    mppt1: Optional[MPPTData] = None
    mppt2: Optional[MPPTData] = None
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
                elif isinstance(field_value, (MPPTData, PhaseData)):
                    # Only include non-empty nested objects
                    if not field_value.is_empty():
                        result[field_name] = field_value.to_dict(verbose)
                else:
                    result[field_name] = field_value
        return result


@dataclass
class BatteryData:
    """Battery system data."""
    name: str = "Battery"
    power: Optional[Value] = None  # Positive when charging, negative when discharging
    current: Optional[Value] = None  # Positive when charging, negative when discharging
    voltage: Optional[Value] = None
    soc: Optional[Value] = None  # State of charge
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
                elif isinstance(field_value, (MPPTData, PhaseData)):
                    # Only include non-empty nested objects
                    if not field_value.is_empty():
                        result[field_name] = field_value.to_dict(verbose)
                else:
                    result[field_name] = field_value
        return result


@dataclass
class MeterData:
    """Meter system data."""
    name: str = "meter"
    active_power: Optional[Value] = None  # Positive when importing, negative when exporting
    frequency: Optional[Value] = None
    l1: Optional[PhaseData] = None
    l2: Optional[PhaseData] = None
    l3: Optional[PhaseData] = None
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
                elif isinstance(field_value, (MPPTData, PhaseData)):
                    # Only include non-empty nested objects
                    if not field_value.is_empty():
                        result[field_name] = field_value.to_dict(verbose)
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
