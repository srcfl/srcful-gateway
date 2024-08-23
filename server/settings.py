import json
import logging
import threading
from typing import Callable, List

from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class DebouncedMonitorBase(ABC):
    def __init__(self, debounce_delay: float = 1.0):
        self.debounce_delay = debounce_delay
        self._debounce_timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()

    def debounce_action(self):
        with self._lock:
            if self._debounce_timer:
                self._debounce_timer.cancel()
            self._debounce_timer = threading.Timer(self.debounce_delay, self._perform_action)
            self._debounce_timer.start()

    @abstractmethod
    def _perform_action(self):
        """
        This method should be overridden by subclasses to define the action
        to be performed after the debounce delay.
        """
        pass

    def on_change(self):
        """
        This method should be called whenever a change occurs that needs to trigger the debounced action.
        """
        logger.info("Change detected")
        self.debounce_action()

class Observable:
    def __init__(self):
        self._listeners: List[Callable[[], None]] = []

    def add_listener(self, listener: Callable[[], None]):
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[], None]):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def notify_listeners(self):
        for listener in self._listeners:
            listener()

class Settings(Observable):
    @property
    def SETTINGS(self):
        return "settings"

    class Harvest(Observable):
        @property
        def HARVEST(self):
            return "harvest"
        
        @property
        def ENDPOINTS(self):
            return "endpoints"

        def __init__(self):
            super().__init__()
            self._endpoints = []

        def add_endpoint(self, endpoint: str):
            if endpoint not in self._endpoints:
                self._endpoints.append(endpoint)
                self.notify_listeners()

        def remove_endpoint(self, endpoint: str):
            if endpoint in self._endpoints:
                self._endpoints.remove(endpoint)
                self.notify_listeners()

        def clear_endpoints(self):
            if len(self._endpoints) > 0:
                self._endpoints.clear()
                self.notify_listeners()

        @property
        def endpoints(self):
            return self._endpoints.copy()

    def __init__(self):
        super().__init__()
        self._harvest = self.Harvest()
        self._harvest.add_listener(self.notify_listeners)

    @property
    def harvest(self) -> Harvest:
        return self._harvest

    def to_json(self) -> str:
        return json.dumps(self.to_dict, indent=4)

    def to_dict(self) -> dict:
        dict = {
            self.SETTINGS: {
                self.harvest.HARVEST: {
                    self.harvest.ENDPOINTS: self.harvest._endpoints
                }
            }
        }
        return dict


    def from_json(self, json_str: str):
        logger.info(f"Settings.from_json: {json_str}")
        dict = json.loads(json_str)
        self.harvest.clear_endpoints()
        for endpoint in dict[self.SETTINGS][self.harvest.HARVEST][self.harvest.ENDPOINTS]:
            self.harvest.add_endpoint(endpoint)
        self.notify_listeners()

    def subscribe_all(self, listener: Callable[[], None]):
        """
        Subscribe the given listener to all Observable objects within this Settings instance.
        """
        self.add_listener(listener)
        self._subscribe_recursive(self, listener)

    def _subscribe_recursive(self, obj, listener: Callable[[], None]):
        for attr_name in dir(obj):
            if attr_name.startswith('_'):
                continue
            attr = getattr(obj, attr_name)
            if isinstance(attr, Observable):
                attr.add_listener(listener)
                self._subscribe_recursive(attr, listener)