from __future__ import annotations

import json
import logging
import threading

from enum import Enum
from typing import Callable, List

from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)

class ChangeSource(Enum):
    LOCAL = 1
    BACKEND = 2


class DebouncedMonitorBase(ABC):
    def __init__(self, debounce_delay: float = 1.0):
        self.debounce_delay = debounce_delay
        self._debounce_timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()

    def debounce_action(self, source: ChangeSource):
        with self._lock:
            if self._debounce_timer:
                self._debounce_timer.cancel()
            self._debounce_timer = threading.Timer(self.debounce_delay, self._perform_action, [source])
            self._debounce_timer.start()

    @abstractmethod
    def _perform_action(self, source: ChangeSource):
        """
        This method should be overridden by subclasses to define the action
        to be performed after the debounce delay.
        """
        pass

    def on_change(self, source: ChangeSource):
        """
        This method should be called whenever a change occurs that needs to trigger the debounced action.
        """
        logger.info("Change detected from %s", source)
        self.debounce_action(source)



class Observable:
    def __init__(self, parent: Optional[Observable] = None):
        self._listeners: List[Callable[[ChangeSource], None]] = []
        self._parent = parent

    def add_listener(self, listener: Callable[[ChangeSource], None]):
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[ChangeSource], None]):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def notify_listeners(self, source: ChangeSource):
        for listener in self._listeners:
            listener(source)
        if self._parent:
            self._parent.notify_listeners(source)



class Settings(Observable):
    def __init__(self):
        super().__init__()
        self._harvest = self.Harvest(self)

    @property
    def API_SUBKEY(self):
        return "settings"

    @property
    def SETTINGS(self):
        return "settings"

    @property
    def harvest(self) -> 'Settings.Harvest':
        return self._harvest

    def update_from_dict(self, data: dict, source: ChangeSource):
        if data and self.SETTINGS in data:
            settings_data = data[self.SETTINGS]
            self.harvest.update_from_dict(settings_data.get(self._harvest.HARVEST, {}), source)

    def to_dict(self) -> dict:
        return {
            self.SETTINGS: {
                self._harvest.HARVEST: self._harvest.to_dict(),
                # ... other settings ...
            }
        }

    def from_json(self, json_str: str, source: ChangeSource):
        data = json.loads(json_str)
        self.update_from_dict(data, source)
        

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    class Harvest(Observable):
        def __init__(self, parent: Optional[Observable] = None):
            super().__init__(parent)
            self._endpoints = []

        @property
        def HARVEST(self):
            return "harvest"
        
        @property
        def ENDPOINTS(self):
            return "endpoints"

        def update_from_dict(self, data: dict, source: ChangeSource ):
            if self.ENDPOINTS in data:
                self._endpoints = data[self.ENDPOINTS]
                self.notify_listeners(source)
                
        def to_dict(self) -> dict:
            return {
                self.ENDPOINTS: self._endpoints
            }

        @property
        def endpoints(self):
            return self._endpoints.copy()

        def add_endpoint(self, endpoint: str, source: ChangeSource):
            if endpoint not in self._endpoints:
                self._endpoints.append(endpoint)
                self.notify_listeners(source)

        def remove_endpoint(self, endpoint: str, source: ChangeSource):
            if endpoint in self._endpoints:
                self._endpoints.remove(endpoint)
                self.notify_listeners(source)

        def clear_endpoints(self, source: ChangeSource):
            if len(self._endpoints) > 0:
                self._endpoints.clear()
                self.notify_listeners(source)   



    def subscribe_all(self, listener: Callable[[ChangeSource], None]):
        """
        Subscribe the given listener to all Observable objects within this Settings instance.
        """
        self.add_listener(listener)
        self._subscribe_recursive(self, listener)

    def _subscribe_recursive(self, obj, listener: Callable[[ChangeSource], None]):
        for attr_name in dir(obj):
            if attr_name.startswith('_'):
                continue
            attr = getattr(obj, attr_name)
            if isinstance(attr, Observable):
                attr.add_listener(listener)
                self._subscribe_recursive(attr, listener)
