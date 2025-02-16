from abc import ABC, abstractmethod
from server.devices.ICom import ICom


class Device(ICom, ABC):
    _is_disconnected: bool = False

    DEVICE_TYPE = "device_type"
    MAKER = "maker"
    DISPLAY_NAME = "display_name"

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

    def get_backoff_time_ms(self, harvest_time_ms: int, previous_backoff_time_ms: int) -> int:
        ''' computes a backoff time based, this is always between 1 and 256 seconds,
        it will increase if the harvest time is high and incrementatlly move towards 1 second if the harvest time is low'''
        min_backoff_time = max(harvest_time_ms * 2, 1000)
        backoff_time = max(int(previous_backoff_time_ms * .9), min_backoff_time)
        backoff_time = min(backoff_time, 256000)
        return backoff_time
    
    def is_open(self) -> bool:
        return self.is_disconnected() != True and self._is_open()

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

    @abstractmethod
    def _is_open(self) -> bool:
        pass

    def get_config(self) -> dict:
        return {
            ICom.CONNECTION_KEY: self._get_connection_type(),
        }

    @abstractmethod
    def _get_connection_type(self) -> str:
        pass

    @staticmethod
    def get_config_schema(connection: str):
        return {ICom.CONNECTION_KEY: f"string - the connection type, for this object use: {connection}"}
