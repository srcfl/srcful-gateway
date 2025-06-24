from enum import Enum
from dataclasses import dataclass


@dataclass
class BaseMeasurement:
    value: float

    def __repr__(self):
        return f"{self.value} {self.unit}"


@dataclass
class Current(BaseMeasurement):
    value: float
    unit: str = "A"


@dataclass
class Voltage(BaseMeasurement):
    value: float
    unit: str = "V"


@dataclass
class Frequency(BaseMeasurement):
    value: float
    unit: str = "Hz"


@dataclass
class Percent(BaseMeasurement):
    value: float
    unit: str = "%"


@dataclass
class Power(BaseMeasurement):
    value: float
    unit: str = "W"


@dataclass
class EBaseType:
    timestamp_ms: int
    device_sn: str


@dataclass
class GridType(EBaseType):
    L1_A: Current
    L2_A: Current
    L3_A: Current
    L1_V: Voltage
    L2_V: Voltage
    L3_V: Voltage


@dataclass
class BatteryType(EBaseType):
    power: Power


@dataclass
class SolarType(EBaseType):
    power: Power


@dataclass
class LoadType(EBaseType):
    power: Power


@dataclass
class ESystemType(EBaseType):
    grid: GridType
    battery: BatteryType
    solar: SolarType
    load: LoadType
