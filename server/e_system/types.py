from enum import Enum
from dataclasses import dataclass


@dataclass
class BaseMeasurement:
    value: float

    def __repr__(self):
        return f"{self.value} {self.unit}"


@dataclass
class Ampere(BaseMeasurement):
    value: float
    unit: str = "A"


@dataclass
class Volt(BaseMeasurement):
    value: float
    unit: str = "V"


@dataclass
class Ohm(BaseMeasurement):
    value: float
    unit: str = "Ω"


@dataclass
class Farad(BaseMeasurement):
    value: float
    unit: str = "F"


@dataclass
class Henry(BaseMeasurement):
    value: float
    unit: str = "H"


@dataclass
class Hertz(BaseMeasurement):
    value: float
    unit: str = "Hz"


@dataclass
class Lux(BaseMeasurement):
    value: float
    unit: str = "lx"


@dataclass
class Lumen(BaseMeasurement):
    value: float
    unit: str = "lm"


@dataclass
class Percent(BaseMeasurement):
    value: float
    unit: str = "%"


@dataclass
class Watt(BaseMeasurement):
    value: float
    unit: str = "W"


@dataclass
class EBaseType:
    timestamp_ms: int
    device_sn: str


@dataclass
class GridType(EBaseType):
    L1_A: Ampere
    L2_A: Ampere
    L3_A: Ampere
    L1_V: Volt
    L2_V: Volt
    L3_V: Volt


@dataclass
class BatteryType(EBaseType):
    power: Watt


@dataclass
class SolarType(EBaseType):
    power: Watt


@dataclass
class LoadType(EBaseType):
    power: Watt


@dataclass
class ESystemType(EBaseType):
    grid: GridType
    battery: BatteryType
    solar: SolarType
    load: LoadType
