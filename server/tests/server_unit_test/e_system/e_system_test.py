from server.e_system.e_system import ESystem
from server.e_system.types import EBatteryType, EPower
import pytest


# @pytest.fixture
# def ebattery():
#     return EBatteryType(device_sn="test", POWER=EPower(value=-100), timestamp_ms=0) # negative power means battery is discharging


# def test_self_consumption_battery(ebattery):
#     esystem = ESystem(battery_sns=[ebattery.device_sn], solar_sns=[], load_sns=[], grid_sns=[], parts=[ebattery])
#     esystem = esystem.self_consumption_battery()
#     assert esystem.get_battery_power().value == 0
