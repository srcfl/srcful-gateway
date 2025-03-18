import server.devices.supported_devices.supported_devices as supported_devices
from server.devices.supported_devices.profiles import ModbusProfile
from server.devices.profile_keys import DeviceCategoryKey
import pytest


@pytest.fixture
def modbus_profiles() -> list[ModbusProfile]:
    profiles: list[ModbusProfile] = []

    # Load inverters
    for device in supported_devices.supported_devices[DeviceCategoryKey.INVERTERS]:
        profiles.append(ModbusProfile(device))

    # Load meters
    for device in supported_devices.supported_devices[DeviceCategoryKey.METERS]:
        profiles.append(ModbusProfile(device))

    return profiles


def test_modbus_profile(modbus_profiles: list[ModbusProfile]):
    pass
