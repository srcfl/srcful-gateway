from __future__ import annotations
import json
import logging
import threading
from typing import Callable, List
from abc import ABC, abstractmethod
from typing import Optional
from server.app.settings.settings_observable import Observable, ChangeSource
from server.app.settings.settings_registry import SettingsRegistry
from server.devices.ICom import ICom
from server.devices.IComFactory import IComFactory


logger = logging.getLogger(__name__)


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


class Settings(Observable):
    def __init__(self):
        super().__init__()
        self._harvest = self.Harvest(self)
        self._devices = self.Devices(self)
        self._api = self.API(self)

        self._modules = SettingsRegistry.create_settings(self)
        
    def __getattr__(self, name: str):
        """Allow accessing registered settings as properties"""
        if name in self._modules:
            return self._modules[name]
        raise AttributeError(f"'Settings' has no attribute '{name}'")

    @property
    def API_SUBKEY(self):
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

            for key, module in self._modules.items():
                if key in settings_data:
                    module.update_from_dict(settings_data[key], source)
            # self.entropy.update_from_dict(settings_data.get(self.entropy.ENTROPY, {}), source)

    def to_dict(self) -> dict:
        ret = {
            self.SETTINGS: {
                key: module.to_dict() for key, module in self._modules.items()
            }
        }

        ret[self.SETTINGS][self.harvest.HARVEST] = self._harvest.to_dict()
        ret[self.SETTINGS][self.devices.DEVICES] = self.devices.to_dict()

        return ret

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
        @property
        def gql_endpoint(self):
            return self._gql_endpoint
        
        @property
        def gql_timeout(self):
            return self._gql_timeout
        
        @property
        def GQL_ENDPOINT(self):
            return "gql_endpoint"
        
        @property
        def GQL_TIMEOUT(self):
            return "gql_timeout"
        
        def to_dict(self) -> dict:
            return {
                self.GQL_ENDPOINT: self._gql_endpoint,
                self.GQL_TIMEOUT: self._gql_timeout
            }
        
        def update_from_dict(self, data: dict, source: ChangeSource):
            notify = False
            if self.GQL_ENDPOINT in data:
                self._gql_endpoint = data[self.GQL_ENDPOINT]
                notify = True
            if self.GQL_TIMEOUT in data:
                self._gql_timeout = data[self.GQL_TIMEOUT]
                notify = True
            if notify:
                self.notify_listeners(source)
        
    class Devices(Observable):
        def __init__(self, parent: Optional[Observable] = None):
            super().__init__(parent)
            self._connections: List[dict] = []


        def add_connection(self, connection: ICom, source: ChangeSource):
            config = connection.get_config()
            if config not in self._connections:

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
            equivalent_configs = [x for x in self._connections if x in self._connections or IComFactory.create_com(x).get_config() in self._connections]

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

    # class Entropy(Observable):
    #     def __init__(self, parent: Optional[Observable] = None):
    #         super().__init__(parent)
    #         self._do_mine = False
    #         self._mqtt_broker = "localhost"
    #         self._mqtt_port = 1883
    #         self._mqtt_topic = "entropy"

    #     @property
    #     def ENTROPY(self):
    #         return "entropy"
        
    #     @property
    #     def DO_MINE(self):
    #         return "do_mine"
        
    #     @property
    #     def MQTT_BROKER(self):
    #         return "mqtt_broker"
        
    #     @property
    #     def MQTT_PORT(self):
    #         return "mqtt_port"
        
    #     @property
    #     def MQTT_TOPIC(self):
    #         return "mqtt_topic"
        

    #     def update_from_dict(self, data: dict, source: ChangeSource):
    #         self._do_mine = data.get(self.DO_MINE, self._do_mine)
    #         self._mqtt_broker = data.get(self.MQTT_BROKER, self._mqtt_broker)
    #         self._mqtt_port = data.get(self.MQTT_PORT, self._mqtt_port)
    #         self._mqtt_topic = data.get(self.MQTT_TOPIC, self._mqtt_topic)
    #         self.notify_listeners(source)
                
    #     def to_dict(self) -> dict:
    #         return {
    #             self.DO_MINE: self._do_mine,
    #             self.MQTT_BROKER: self._mqtt_broker,
    #             self.MQTT_PORT: self._mqtt_port,
    #             self.MQTT_TOPIC: self._mqtt_topic
    #         }

    #     @property
    #     def do_mine(self):
    #         return self._do_mine
        
    #     @property
    #     def mqtt_broker(self):
    #         return self._mqtt_broker
        
    #     @property
    #     def mqtt_port(self):
    #         return self._mqtt_port
        
    #     @property
    #     def mqtt_topic(self):
    #         return self._mqtt_topic
        
    #     def set_do_mine(self, do_mine: bool, source: ChangeSource):
    #         self._do_mine = do_mine
    #         self.notify_listeners(source)

    #     def set_mqtt_broker(self, mqtt_broker: str, source: ChangeSource):
    #         self._mqtt_broker = mqtt_broker
    #         self.notify_listeners(source)

    #     def set_mqtt_port(self, mqtt_port: int, source: ChangeSource):
    #         self._mqtt_port = mqtt_port
    #         self.notify_listeners(source)

    #     def set_mqtt_topic(self, mqtt_topic: str, source: ChangeSource):
    #         self._mqtt_topic = mqtt_topic
    #         self.notify_listeners(source)

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
