from abc import ABC, abstractmethod
from enum import Enum
import uuid
from server.devices.ICom import ICom
from server.devices.DeeDecoder import DeeDecoder, SungrowDeeDecoder
from typing import Any

class DeviceMode(Enum):
    NONE = "none"
    READ = "read"
    CONTROL = "control"

class DeviceCommandType(Enum):
    SET_BATTERY_POWER = "set_battery_power"

class DeviceCommandStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"

class DeviceCommand:
    def __init__(self, command_type: DeviceCommandType, value: Any):
        self.command_type = command_type
        self.values:list[Any] = []
        self.values.append(value)

        self.id = str(uuid.uuid4())
        self.success = DeviceCommandStatus.PENDING
        self.ts_executed = 0

    
class Device(ICom, ABC):
    _is_disconnected: bool = False

    DEVICE_TYPE = "device_type"
    MAKER = "maker"
    DISPLAY_NAME = "display_name"


    def __init__(self):
        super().__init__()
        self._last_harvest_data = {}
        self._mode = DeviceMode.READ
        self.commands = []

    def add_command(self, command: DeviceCommand) -> None:
        self.commands.append(command)

    def pop_command(self) -> DeviceCommand:
        return self.commands.pop(0)
    
    def has_commands(self) -> bool:
        return len(self.commands) > 0

    def set_mode(self, state: DeviceMode) -> None:
        # override in subclasses to allow controll
        self._mode = DeviceMode.READ

    def get_mode(self) -> DeviceMode:
        return self._mode

    def is_disconnected(self) -> bool:
        return self._is_disconnected

    def disconnect(self) -> None:
        self._is_disconnected = True
        self._disconnect()

    def connect(self, **kwargs) -> bool:
        if self.is_disconnected() != True:
            return self._connect(**kwargs)
        return False
    
    def get_dee_decoder(self) -> DeeDecoder:
        return SungrowDeeDecoder()

    def get_last_harvest_data(self) -> dict:
        return self._last_harvest_data

    def read_harvest_data(self, force_verbose) -> dict:
        if self.is_disconnected() != True:
            self._last_harvest_data = self._read_harvest_data(force_verbose)
            return self._last_harvest_data

        raise Exception("Device is disconnected")

    def get_backoff_time_ms(self, harvest_time_ms: int, previous_backoff_time_ms: int) -> int:
        ''' computes a backoff time based, this is always between 1 and 256 seconds,
        it will increase if the harvest time is high and incrementatlly move towards 1000ms if the harvest time is low'''
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
