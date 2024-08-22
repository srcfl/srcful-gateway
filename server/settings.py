import json
import logging
from typing import Callable, List

logger = logging.getLogger(__name__)

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

    def to_json(self):
        dict = {
            self.SETTINGS: {
                self.harvest.HARVEST: {
                    self.harvest.ENDPOINTS: self.harvest._endpoints
                }
            }
        }
        return json.dumps(dict, indent=4)

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