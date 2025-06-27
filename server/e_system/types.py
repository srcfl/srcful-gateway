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
    rated_power: EPower


@dataclass(frozen=True, eq=True)
class EGridType(EBaseType):
    l1_A: ECurrent  # Must be in A. Positive for import, negative for export
    l2_A: ECurrent  # Must be in A. Positive for import, negative for export
    l3_A: ECurrent  # Must be in A.
    l1_V: EVoltage  # Must be in V.
    l2_V: EVoltage  # Must be in V.
    l3_V: EVoltage  # Must be in V.
    l1_P: EPower  # Must be in W. Positive for import, negative for export
    l2_P: EPower  # Must be in W. Positive for import, negative for export
    l3_P: EPower  # Must be in W. Positive for import, negative for export
    grid_frequency: EFrequency  # Must be in Hz.
    total_import_energy: EEnergy  # Must be in Wh.
    total_export_energy: EEnergy  # Must be in Wh.

    def total_power(self) -> EPower:
        return EPower(self.l1_P.value + self.l2_P.value + self.l3_P.value)


@dataclass(frozen=True, eq=True)
class EBatteryType(EBaseType):
    power: EPower  # Must be in W. Positive for charge, negative for discharge
    current: ECurrent  # Must be in A. Positive for charge, negative for discharge
    voltage: EVoltage  # Must be in V.
    soc: EPercent  # Must be in %.
    capacity: EEnergy  # Must be in Wh.
    temperature: ETemperature  # Must be in °C.
    total_charge_energy: EPower  # Must be in Wh.
    total_discharge_energy: EPower  # Must be in Wh.


@dataclass(frozen=True, eq=True)
class ESolarType(EBaseType):
    power: EPower  # Must be in W. Always negative.
    temperature: ETemperature  # Must be in °C.
    total_pv_energy: EEnergy  # Must be in Wh. Always negative.


@dataclass(frozen=True, eq=True)
class ELoadType(EBaseType):
    power: EPower  # Must be in W.
