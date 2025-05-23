from abc import ABC, abstractmethod


class BaseDefinition(ABC):

    @abstractmethod
    def get_profile(self) -> dict:
        """
        This method is used to get the profile of the device.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def definition_is_valid(self, definition: dict) -> bool:
        """
        This method is used to check if the definition is valid.
        It can for example check if it is possible to retrieve the serial number or other values from the device.
        """
        raise NotImplementedError("Subclasses must implement this method")
