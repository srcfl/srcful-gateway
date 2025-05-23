import typing
from ..profile_keys import ProfileKey, RegistersKey, DeviceCategoryKey, ProtocolKey, EndiannessKey, FunctionCodeKey
from ..profile_keys import DataTypeKey
from .supported_devices import supported_devices_profiles
from abc import ABC
from typing import List
from .profile import DeviceProfile, ModbusProfile


class ModbusDeviceProfiles:
    """Device profiles class. Used to load and manage device profiles."""

    def __init__(self, device_category: DeviceCategoryKey = DeviceCategoryKey.INVERTERS):
        self.profiles: list[DeviceProfile] = []
        self._load_profiles()

    def _load_profiles(self):
        for profile in supported_devices_profiles:
            self.profiles.append(profile)

    def _create_profile(self, profile_data: dict) -> DeviceProfile:
        protocol = profile_data[ProfileKey.PROTOCOL]

        if protocol == ProtocolKey.MODBUS or protocol == ProtocolKey.SOLARMAN:
            return ModbusProfile(profile_data)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    def get(self, name: str) -> DeviceProfile | None:
        for profile in self.profiles:
            if profile.name.lower() == name.lower():
                return profile
        return None

    def get_supported_devices(self) -> typing.List[DeviceProfile]:
        return self.profiles.copy()
