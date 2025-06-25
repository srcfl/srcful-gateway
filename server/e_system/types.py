from enum import Enum
from dataclasses import dataclass


class EUnit(Enum):
    A = "A"
    V = "V"
    Hz = "Hz"
    Percent = "%"
    W = "W"

@dataclass(frozen=True, eq=True)
class EBaseMeasurement:
    value: float
    unit: EUnit

    def __repr__(self):
        return f"{self.value} {self.unit}"
    
@dataclass(frozen=True, eq=True)
class ECurrent(EBaseMeasurement):
    unit: EUnit = EUnit.A


@dataclass(frozen=True, eq=True)
class EVoltage(EBaseMeasurement):
    unit: EUnit = EUnit.V


@dataclass(frozen=True, eq=True)
class EFrequency(EBaseMeasurement):
    unit: EUnit = EUnit.Hz


@dataclass(frozen=True, eq=True)
class EPercent(EBaseMeasurement):
    unit: EUnit = EUnit.Percent


@dataclass(frozen=True, eq=True)
class EPower(EBaseMeasurement):
    unit: EUnit = EUnit.W


@dataclass(frozen=True, eq=True)
class EBaseType:
    timestamp_ms: int
    device_sn: str


@dataclass(frozen=True, eq=True)
class EGridType(EBaseType):
    L1_A: ECurrent
    L2_A: ECurrent
    L3_A: ECurrent
    L1_V: EVoltage
    L2_V: EVoltage
    L3_V: EVoltage

    def total_power(self) -> EPower:
        return EPower(self.L1_A.value * self.L1_V.value + self.L2_A.value * self.L2_V.value + self.L3_A.value * self.L3_V.value)


@dataclass(frozen=True, eq=True)
class EBatteryType(EBaseType):
    power: EPower


@dataclass(frozen=True, eq=True)
class ESolarType(EBaseType):
    power: EPower


@dataclass(frozen=True, eq=True)
class ELoadType(EBaseType):
    power: EPower
