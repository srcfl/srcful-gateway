from abc import ABC, abstractmethod


class BaseProfile(ABC):

    @abstractmethod
    def get_profile(self) -> dict:
        """
        This method is used to get the profile of the device.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def profile_is_valid(self, profile: dict) -> bool:
        """
        This method is used to check if the profile is valid.
        It can for example check if it is possible to retrieve the serial number or other values from the device.
        """
        raise NotImplementedError("Subclasses must implement this method")
