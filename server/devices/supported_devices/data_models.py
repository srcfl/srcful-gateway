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
class PVData:
    """Photovoltaic system data with flattened structure."""
    type: str = "PV"
    make: Optional[str] = None  # Manufacturer/brand (e.g., "Deye", "Huawei", "Solis", "SunGrow")
    timestamp: Optional[int] = None  # Timestamp
    delta: Optional[int] = None  # Reading duration in milliseconds
    W: Optional[float] = None  # Active Power (always negative for generation)
    rating: Optional[float] = None  # Active Power Max Rating (from model 702)
    HV_LV: Optional[float] = None  # High/Low voltage indicator
    # MPPT1 data - flattened
    mppt1_V: Optional[float] = None  # MPPT1 Voltage (DCV in SunSpec DC model)
    mppt1_A: Optional[float] = None  # MPPT1 Current (DCA in SunSpec DC model)
    # MPPT2 data - flattened
    mppt2_V: Optional[float] = None  # MPPT2 Voltage (DCV in SunSpec DC model)
    mppt2_A: Optional[float] = None  # MPPT2 Current (DCA in SunSpec DC model)
    # Temperature data - flattened
    heatsink_C: Optional[float] = None  # Heat Sink Temperature (inverter temperature)
    # Total energy data - flattened
    total_export_Wh: Optional[float] = None  # Total Energy Generated
    total_import_Wh: Optional[float] = None  # Total Energy Imported
    total_uptime_s: Optional[float] = None  # System uptime

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                result[field_name] = field_value
        return result


@dataclass
class BatteryData:
    """Battery system data with flattened structure."""
    type: str = "Battery"
    make: Optional[str] = None  # Manufacturer/brand (e.g., "Deye", "Huawei", "Solis", "SunGrow")
    timestamp: Optional[int] = None  # Timestamp
    delta: Optional[int] = None  # Reading duration in milliseconds
    W: Optional[float] = None  # Active Power (positive charging, negative discharging)
    A: Optional[float] = None  # Current (positive charging, negative discharging)
    V: Optional[float] = None  # Voltage
    # State of Charge data - flattened
    SoC_nom_fract: Optional[float] = None  # State of Charge as fraction (0.0-1.0)
    # Temperature data - flattened
    heatsink_C: Optional[float] = None  # Battery Temperature
    # Total energy data - flattened
    total_export_Wh: Optional[float] = None  # Total Energy Discharged
    total_import_Wh: Optional[float] = None  # Total Energy Charged
    total_uptime_s: Optional[float] = None  # System uptime

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                result[field_name] = field_value
        return result


@dataclass
class MeterData:
    """Meter system data with flattened structure."""
    type: str = "Meter"
    make: Optional[str] = None  # Manufacturer/brand (e.g., "Deye", "Huawei", "Solis", "SunGrow")
    timestamp: Optional[int] = None  # Timestamp
    delta: Optional[int] = None  # Reading duration in milliseconds
    W: Optional[float] = None  # Total Active Power (positive importing, negative exporting)
    Hz: Optional[float] = None  # Frequency
    # L1 phase data - flattened
    L1_V: Optional[float] = None  # L1 Phase Voltage
    L1_A: Optional[float] = None  # L1 Phase Current
    L1_W: Optional[float] = None  # L1 Phase Power
    # L2 phase data - flattened
    L2_V: Optional[float] = None  # L2 Phase Voltage
    L2_A: Optional[float] = None  # L2 Phase Current
    L2_W: Optional[float] = None  # L2 Phase Power
    # L3 phase data - flattened
    L3_V: Optional[float] = None  # L3 Phase Voltage
    L3_A: Optional[float] = None  # L3 Phase Current
    L3_W: Optional[float] = None  # L3 Phase Power
    # Total energy data - flattened
    total_export_Wh: Optional[float] = None  # Total Energy Exported
    total_import_Wh: Optional[float] = None  # Total Energy Imported
    total_uptime_s: Optional[float] = None  # System uptime

    def to_dict(self, verbose: bool = True) -> Dict[str, Any]:
        """Convert to dictionary format for serialization."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                result[field_name] = field_value
        return result


@dataclass
class DERData:
    """Complete Distributed Energy Resource data model."""

    def __init__(self, pv: Optional[PVData] = None, battery: Optional[BatteryData] = None, meter: Optional[MeterData] = None):
        self.pv = pv
        self.battery = battery
        self.meter = meter
        self.version = "v0"
        self.format = "unknown"


    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for serialization, including version and format."""
        result = {}
        if self.pv is not None:
            result["pv"] = self.pv.to_dict()
        if self.battery is not None:
            result["battery"] = self.battery.to_dict()
        if self.meter is not None:
            result["meter"] = self.meter.to_dict()
        result["version"] = self.version
        result["format"] = self.format
        return result
    
    def get_ders(self) -> List[PVData | BatteryData | MeterData]:
        return [der for der in [self.pv, self.battery, self.meter] if der is not None]

    def is_empty(self) -> bool:
        """Check if all data sections are empty."""
        return self.pv is None and self.battery is None and self.meter is None
