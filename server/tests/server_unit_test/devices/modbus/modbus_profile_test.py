import server.devices.supported_devices.supported_devices as supported_devices
from server.devices.supported_devices.profiles import ModbusProfile
from server.devices.profile_keys import DeviceCategoryKey
import pytest


@pytest.fixture
def modbus_profiles() -> list[ModbusProfile]:
    profiles: list[ModbusProfile] = []

    # Load inverters
    for device_profile_obj in supported_devices.supported_devices:
        profile = ModbusProfile(device_profile_obj.get_profile())
        profiles.append(profile)

    return profiles


def test_modbus_profile(modbus_profiles: list[ModbusProfile]):
    for profile in modbus_profiles:
        assert profile.name is not None
        assert profile.maker is not None
        assert profile.version is not None
        assert profile.verbose_always is not None
        assert profile.display_name is not None
        assert profile.protocol is not None
        assert profile.description is not None
        assert profile.always_include is not None

        # assert profile.sn is not None

        assert profile.registers is not None
        assert profile.registers_verbose is not None

        assert profile.keywords is not None
