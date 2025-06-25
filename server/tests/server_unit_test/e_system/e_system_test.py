from server.e_system.e_system import ESystem
from server.e_system.types import EBatteryType, EPower, ELoadType
import pytest


@pytest.fixture
def ebattery():
    return EBatteryType(device_sn="test", power=EPower(value=-200), timestamp_ms=0) # negative power means battery is discharging

@pytest.fixture
def eload():
    return ELoadType(device_sn="test", power=EPower(value=100), timestamp_ms=0) # positive power means load is consuming power (as is always should be)

def test_self_consumption_battery(ebattery, eload):
    esystem = ESystem(battery_sns=[ebattery.device_sn], solar_sns=[], load_sns=[eload.device_sn], grid_sns=[], parts=[ebattery, eload])
    esystem = esystem.self_consumption_battery()
    assert esystem.get_battery_power().value == -100 
