from enum import Enum
from dataclasses import dataclass, asdict


def _convert_enum_values(obj):
    """Recursively convert enum values to their string representations"""
    if isinstance(obj, dict):
        return {key: _convert_enum_values(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_enum_values(item) for item in obj]
    elif isinstance(obj, Enum):
        return obj.value
    else:
        return obj


class EUnit(Enum):
    A = "A"
    V = "V"
    Hz = "Hz"
    Percent = "%"
    W = "W"
    C = "C"
    Wh = "Wh"


@dataclass(frozen=True, eq=True)
class EBaseMeasurement:
    value: float
    unit: EUnit

    def __repr__(self):
        return f"{self.value} {self.unit.value}"

    def to_dict(self):
        return _convert_enum_values(asdict(self))


@dataclass(frozen=True, eq=True)
class ETemperature(EBaseMeasurement):
    unit: EUnit = EUnit.C


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
class EEnergy(EBaseMeasurement):
    unit: EUnit = EUnit.Wh


@dataclass(frozen=True, eq=True)
class EBaseType:
    timestamp_ms: int
    device_sn: str

    def to_dict(self):
        result = _convert_enum_values(asdict(self))
        result["type"] = self.__class__.__name__
        return result


@dataclass(frozen=True, eq=True)
class EMetadata(EBaseType):
    model: str
    rated_power: int


@dataclass(frozen=True, eq=True)
class EGridType(EBaseType):
    L1_A: ECurrent  # Must be in A. Positive for import, negative for export
    L2_A: ECurrent  # Must be in A. Positive for import, negative for export
    L3_A: ECurrent  # Must be in A.
    L1_V: EVoltage  # Must be in V.
    L2_V: EVoltage  # Must be in V.
    L3_V: EVoltage  # Must be in V.
    L1_P: EPower  # Must be in W. Positive for import, negative for export
    L2_P: EPower  # Must be in W. Positive for import, negative for export
    L3_P: EPower  # Must be in W. Positive for import, negative for export
    GRID_FREQUENCY: EFrequency  # Must be in Hz.
    TOTAL_IMPORT_ENERGY: EEnergy  # Must be in Wh.
    TOTAL_EXPORT_ENERGY: EEnergy  # Must be in Wh.

    def total_power(self) -> EPower:
        return EPower(self.L1_P.value + self.L2_P.value + self.L3_P.value)


@dataclass(frozen=True, eq=True)
class EBatteryType(EBaseType):
    POWER: EPower  # Must be in W. Positive for charge, negative for discharge
    CURRENT: ECurrent  # Must be in A. Positive for charge, negative for discharge
    VOLTAGE: EVoltage  # Must be in V.
    SOC: EPercent  # Must be in %.
    CAPACITY: EEnergy  # Must be in Wh.
    TEMPERATURE: ETemperature  # Must be in °C.
    TOTAL_CHARGE_ENERGY: EPower  # Must be in Wh.
    TOTAL_DISCHARGE_ENERGY: EPower  # Must be in Wh.


@dataclass(frozen=True, eq=True)
class ESolarType(EBaseType):
    POWER: EPower  # Must be in W. Always negative.
    TEMPERATURE: ETemperature  # Must be in °C.
    TOTAL_PV_ENERGY: EEnergy  # Must be in Wh. Always negative.


@dataclass(frozen=True, eq=True)
class ELoadType(EBaseType):
    POWER: EPower  # Must be in W.
