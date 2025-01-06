from __future__ import annotations
import json
import logging
import threading
from enum import Enum
from typing import Callable, List
from abc import ABC, abstractmethod
from typing import Optional
from server.devices.ICom import ICom
from server.devices.IComFactory import IComFactory


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
        self._devices = self.Devices(self)
        self._api = self.API(self)
    @property
    def API_SUBKEY(self):
        return "settings"
    
    @property
    def SETTINGS_SUBKEY(self):
        return "settings"
    
    @property
    def SETTINGS(self):
        return "settings"

    @property
    def harvest(self) -> 'Settings.Harvest':
        return self._harvest

    @property
    def devices(self) -> 'Settings.Devices':
        return self._devices
    
    @property
    def api(self) -> 'Settings.API':
        return self._api

    def update_from_dict(self, data: dict, source: ChangeSource):
        if data and self.SETTINGS in data:
            settings_data = data[self.SETTINGS]
            self.harvest.update_from_dict(settings_data.get(self.harvest.HARVEST, {}), source)
            self.devices.update_from_dict(settings_data.get(self.devices.DEVICES, {}), source)
            self.api.update_from_dict(settings_data.get(self.api.API, {}), source)
            
    def to_dict(self) -> dict:
        return {
            self.SETTINGS: {
                self.harvest.HARVEST: self._harvest.to_dict(),
                self.devices.DEVICES: self.devices.to_dict(),
                self.api.API: self.api.to_dict()
            }
        }

    def from_json(self, json_str: str, source: ChangeSource):
        data = json.loads(json_str)
        self.update_from_dict(data, source)
        

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    class API(Observable):
        def __init__(self, parent: Optional[Observable] = None):
            super().__init__(parent)
            self._gql_endpoint = "https://api.srcful.dev"
            self._gql_timeout = 5
            self._ws_endpoint = "wss://api.srcful.dev"

        @property
        def API(self):
            return "api"
        
        @property
        def gql_endpoint(self):
            return self._gql_endpoint
        
        def set_gql_endpoint(self, value: str, change_source: ChangeSource):
            self._gql_endpoint = value
            self.notify_listeners(change_source)
        
        @property
        def ws_endpoint(self):
            return self._ws_endpoint
        
        def set_ws_endpoint(self, value: str, change_source: ChangeSource):
            self._ws_endpoint = value
            self.notify_listeners(change_source)
        
        @property
        def gql_timeout(self):
            return self._gql_timeout
        
        def set_gql_timeout(self, value: int, change_source: ChangeSource):
            self._gql_timeout = value
            self.notify_listeners(change_source)
        
        @property
        def GQL_ENDPOINT(self):
            return "gql_endpoint"
        
        @property
        def WS_ENDPOINT(self):
            return "ws_endpoint"
        
        @property
        def GQL_TIMEOUT(self):
            return "gql_timeout"
              
        def to_dict(self) -> dict:
            return {
                self.GQL_ENDPOINT: self._gql_endpoint,
                self.GQL_TIMEOUT: self._gql_timeout,
                self.WS_ENDPOINT: self._ws_endpoint
            }
        
        def update_from_dict(self, data: dict, source: ChangeSource):
            notify = False
            if self.GQL_ENDPOINT in data:
                self._gql_endpoint = data[self.GQL_ENDPOINT]
                notify = True
            if self.GQL_TIMEOUT in data:
                self._gql_timeout = data[self.GQL_TIMEOUT]
                notify = True
            if self.WS_ENDPOINT in data:
                self._ws_endpoint = data[self.WS_ENDPOINT]
                notify = True
            if notify:
                self.notify_listeners(source)
        
    class Devices(Observable):
        def __init__(self, parent: Optional[Observable] = None):
            super().__init__(parent)
            self._connections: List[dict] = []


        def add_connection(self, connection: ICom, source: ChangeSource):
            config = connection.get_config()
            # if config not in self._connections:

            # Remove old configs that are the same either the same host or the same serial number
            old_configs = [x for x in self._connections if connection.compare_host(IComFactory.create_com(x)) or connection.get_SN() == IComFactory.create_com(x).get_SN()]

            for old_config in old_configs:
                self._connections.remove(old_config)

            self._connections.append(config)
            self.notify_listeners(source)

        def remove_connection(self, connection: ICom, source: ChangeSource):
            config = connection.get_config()
            removed = False

            # configurations may change format between version, so we need to check for equivalent configs
            equivalent_configs = [x for x in self._connections if config == x or IComFactory.create_com(x).get_config() == config]

            for equivalent_config in equivalent_configs:
                self._connections.remove(equivalent_config)

            # notify if something was removed
            if len(equivalent_configs) > 0:
                self.notify_listeners(source)

        @property
        def CONNECTIONS(self):
            return "connections"
        
        @property
        def DEVICES(self):
            return "devices"
    
        @property
        def connections(self):
            return self._connections
        
        def to_dict(self) -> dict:
            return {
                self.CONNECTIONS: self._connections
            }
        
        def update_from_dict(self, data: dict, source: ChangeSource):
            if self.CONNECTIONS in data:
                self._connections = data[self.CONNECTIONS]
                self.notify_listeners(source)
    
    

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
