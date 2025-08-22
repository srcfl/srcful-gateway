from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List


class Unit(str, Enum):
    W = "W"
    V = "V"
    A = "A"
    Hz = "Hz"
    C = "°C"
    PERCENT = "%"
    Wh = "Wh"
    VA = "VA"
    VAR = "VAR"
    PF = "PF"


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
    """MPPT (Maximum Power Point Tracker) data following SunSpec naming."""
    V: Optional[float] = None  # Voltage (DCV in SunSpec DC model)
    A: Optional[float] = None  # Current (DCA in SunSpec DC model)

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                result[field_name] = field_value
        return result

    def is_empty(self) -> bool:
        """Check if this MPPT has any data."""
        return self.V is None and self.A is None


@dataclass
class PhaseData:
    """Single phase electrical measurements following SunSpec naming."""
    V: Optional[float] = None  # Phase Voltage (VL1, VL2, VL3 in SunSpec)
    A: Optional[float] = None  # Phase Current (AL1, AL2, AL3 in SunSpec)
    W: Optional[float] = None  # Active Power (WL1, WL2, WL3 in SunSpec)

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                result[field_name] = field_value
        return result

    def is_empty(self) -> bool:
        """Check if this phase has any data."""
        return self.V is None and self.A is None and self.W is None


@dataclass
class EnergyData:
    """Energy measurement data."""
    Wh: Optional[float] = None

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        if self.Wh is not None:
            result["Wh"] = self.Wh
        return result

    def is_empty(self) -> bool:
        """Check if this energy has any data."""
        return self.Wh is None


@dataclass
class UptimeData:
    """Uptime measurement data."""
    s: Optional[float] = None

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        if self.s is not None:
            result["s"] = self.s
        return result

    def is_empty(self) -> bool:
        """Check if this uptime has any data."""
        return self.s is None


@dataclass
class TotalEnergyData:
    """Total energy measurements with import/export structure."""
    import_: Optional[EnergyData] = None  # Energy imported/absorbed
    export: Optional[EnergyData] = None  # Energy exported/injected
    uptime: Optional[UptimeData] = None  # System uptime

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        if self.import_ is not None and not self.import_.is_empty():
            result["import"] = self.import_.to_dict(verbose)
        if self.export is not None and not self.export.is_empty():
            result["export"] = self.export.to_dict(verbose)
        if self.uptime is not None and not self.uptime.is_empty():
            result["uptime"] = self.uptime.to_dict(verbose)
        return result

    def is_empty(self) -> bool:
        """Check if this total energy has any data."""
        return ((self.import_ is None or self.import_.is_empty()) and 
                (self.export is None or self.export.is_empty()) and
                (self.uptime is None or self.uptime.is_empty()))


@dataclass
class NominalData:
    """Nominal measurement data."""
    fract: Optional[float] = None

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        if self.fract is not None:
            result["fract"] = self.fract
        return result

    def is_empty(self) -> bool:
        """Check if this nominal has any data."""
        return self.fract is None


@dataclass
class SoCData:
    """State of Charge measurement data."""
    nom: Optional[NominalData] = None

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        if self.nom is not None and not self.nom.is_empty():
            result["nom"] = self.nom.to_dict(verbose)
        return result

    def is_empty(self) -> bool:
        """Check if this SoC has any data."""
        return self.nom is None or self.nom.is_empty()


@dataclass
class TemperatureData:
    """Temperature measurement data."""
    C: Optional[float] = None

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        if self.C is not None:
            result["C"] = self.C
        return result

    def is_empty(self) -> bool:
        """Check if this temperature has any data."""
        return self.C is None


@dataclass
class PVData:
    """Photovoltaic system data following SunSpec naming."""
    type: str = "PV"
    make: Optional[str] = None  # Manufacturer/brand (e.g., "Deye", "Huawei", "Solis", "SunGrow")
    ts: Optional[int] = None  # Timestamp
    reading_duration_ms: Optional[int] = None  # Reading duration in milliseconds
    W: Optional[float] = None  # Active Power (always negative for generation)
    rated_power: Optional[float] = None  # Active Power Max Rating (from model 702)
    HV_LV: Optional[float] = None  # High/Low voltage indicator
    MPPT1: Optional[MPPTData] = None  # MPPT 1 data
    MPPT2: Optional[MPPTData] = None  # MPPT 2 data
    heatsink_tmp: Optional[TemperatureData] = None  # Heat Sink Temperature (inverter temperature)
    total: Optional[TotalEnergyData] = None  # Total energy data

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                if isinstance(field_value, (float, int, str)):
                    result[field_name] = field_value
                elif isinstance(field_value, (MPPTData, PhaseData, TotalEnergyData, TemperatureData)):
                    # Only include non-empty nested objects
                    if not field_value.is_empty():
                        result[field_name] = field_value.to_dict(verbose)
                else:
                    result[field_name] = field_value
        return result


@dataclass
class BatteryData:
    """Battery system data following SunSpec naming."""
    type: str = "Battery"
    make: Optional[str] = None  # Manufacturer/brand (e.g., "Deye", "Huawei", "Solis", "SunGrow")
    ts: Optional[int] = None  # Timestamp
    reading_duration_ms: Optional[int] = None  # Reading duration in milliseconds
    W: Optional[float] = None  # Active Power (positive charging, negative discharging)
    A: Optional[float] = None  # Current (positive charging, negative discharging)
    V: Optional[float] = None  # Voltage
    SoC: Optional[SoCData] = None  # State of Charge
    Tmp: Optional[TemperatureData] = None  # Battery Temperature
    total: Optional[TotalEnergyData] = None  # Total energy data

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                if isinstance(field_value, (float, int, str)):
                    result[field_name] = field_value
                elif isinstance(field_value, (MPPTData, PhaseData, TotalEnergyData, SoCData, TemperatureData)):
                    # Only include non-empty nested objects
                    if not field_value.is_empty():
                        result[field_name] = field_value.to_dict(verbose)
                else:
                    result[field_name] = field_value
        return result


@dataclass
class MeterData:
    """Meter system data following SunSpec naming."""
    type: str = "Meter"
    make: Optional[str] = None  # Manufacturer/brand (e.g., "Deye", "Huawei", "Solis", "SunGrow")
    ts: Optional[int] = None  # Timestamp
    reading_duration_ms: Optional[int] = None  # Reading duration in milliseconds
    W: Optional[float] = None  # Total Active Power (positive importing, negative exporting)
    Hz: Optional[float] = None  # Frequency
    L1: Optional[PhaseData] = None  # Phase L1 data
    L2: Optional[PhaseData] = None  # Phase L2 data
    L3: Optional[PhaseData] = None  # Phase L3 data
    total: Optional[TotalEnergyData] = None  # Total energy data

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                if isinstance(field_value, (float, int, str)):
                    result[field_name] = field_value
                elif isinstance(field_value, (MPPTData, PhaseData, TotalEnergyData)):
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
            result["pv"] = self.pv.to_dict()
        if self.battery is not None:
            result["battery"] = self.battery.to_dict()
        if self.meter is not None:
            result["meter"] = self.meter.to_dict()
        return result
    
    def get_ders(self) -> List[PVData | BatteryData | MeterData]:
        return [der for der in [self.pv, self.battery, self.meter] if der is not None]

    def is_empty(self) -> bool:
        """Check if all data sections are empty."""
        return self.pv is None and self.battery is None and self.meter is None
