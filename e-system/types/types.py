from enum import Enum
from dataclasses import dataclass


class MeasurementUnit(Enum):
    AMPERE = "A"
    VOLT = "V"
    OHM = "Ω"
    FARAD = "F"
    HENRY = "H"
    HERTZ = "Hz"
    LUX = "lx"
    LUMEN = "lm"
    PERCENT = "%"
    WATT = "W"  # Added since you're using power measurements


@dataclass
class Measurement:
    value: float
    unit: MeasurementUnit

    def __repr__(self):
        return f"{self.value} {self.unit.value}"


@dataclass
class BaseType:
    timestamp_ms: int
    device_sn: str


@dataclass
class GridType(BaseType):
    L1_A: Measurement
    L2_A: Measurement
    L3_A: Measurement
    L1_V: Measurement
    L2_V: Measurement
    L3_V: Measurement


@dataclass
class BatteryType(BaseType):
    power: Measurement


@dataclass
class SolarType(BaseType):
    power: Measurement


@dataclass
class LoadType(BaseType):
    power: Measurement
