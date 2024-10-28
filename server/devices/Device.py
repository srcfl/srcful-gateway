from abc import ABC, abstractmethod

from server.devices.ICom import ICom


class Device(ICom, ABC):
    _is_disconnected: bool = False

    def __init__(self):
        super().__init__()

    def is_disconnected(self) -> bool:
        return self._is_disconnected
    
    def disconnect(self) -> None:
        self._is_disconnected = True
        self._disconnect()

    def connect(self, **kwargs) -> bool:
        if self.is_disconnected() != True:
            return self._connect(**kwargs)
        return False
    
    def read_harvest_data(self, force_verbose) -> dict:
        if self.is_disconnected() != True:
            return self._read_harvest_data(force_verbose)

        raise Exception("Device is disconnected")

    @abstractmethod
    def _read_harvest_data(self, force_verbose) -> dict:
        pass

    @abstractmethod
    def _disconnect(self) -> None:
        '''Implementation of device specific disconnect'''
        pass

    @abstractmethod
    def _connect(self, **kwargs) -> bool:
        '''Implementation of device specific connection'''
        pass
