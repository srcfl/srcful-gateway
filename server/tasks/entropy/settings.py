from typing import Dict, Optional
from server.app.settings import Observable, ChangeSource
from server.app.settings_registry import SettingsRegistry

class EntropySettings(Observable):
    """Entropy settings with observable properties"""
    ENTROPY = "entropy"
    DO_MINE = "do_mine"
    MQTT_BROKER = "mqtt_broker"
    MQTT_PORT = "mqtt_port"
    MQTT_TOPIC = "mqtt_topic"

    def __init__(self, parent: Optional[Observable] = None):
        super().__init__(parent)
        # Private attributes with defaults
        self._do_mine = False
        self._mqtt_broker = "aumwfe410clfv-ats.iot.us-east-1.amazonaws.com"
        self._mqtt_port = 8883
        self._mqtt_topic = "entropy/srcful"

        # self._settings.entropy.set_do_mine(True, ChangeSource.LOCAL)
        # self._settings.entropy.set_mqtt_broker("aumwfe410clfv-ats.iot.us-east-1.amazonaws.com", ChangeSource.LOCAL)
        # self._settings.entropy.set_mqtt_port(8883, ChangeSource.LOCAL)
        # self._settings.entropy.set_mqtt_topic("entropy/srcful", ChangeSource.LOCAL)

    @property
    def do_mine(self) -> bool:
        return self._do_mine

    def set_do_mine(self, value: bool, source: ChangeSource):
        self._do_mine = value
        self.notify_listeners(source)

    @property
    def mqtt_broker(self) -> str:
        return self._mqtt_broker
    
    def set_mqtt_broker(self, value: str, source: ChangeSource):
        self._mqtt_broker = value
        self.notify_listeners(source)

    @property
    def mqtt_port(self) -> int:
        return self._mqtt_port
    
    def set_mqtt_port(self, value: int, source: ChangeSource):
        self._mqtt_port = value
        self.notify_listeners(source)

    @property
    def mqtt_topic(self) -> str:
        return self._mqtt_topic

    def set_mqtt_topic(self, value: str, source: ChangeSource):
        self._mqtt_topic = value
        self.notify_listeners(source)

    def update_from_dict(self, data: Dict, source: ChangeSource):
        if self.DO_MINE in data:
            self._do_mine = data[self.DO_MINE]
        if self.MQTT_BROKER in data:
            self._mqtt_broker = data[self.MQTT_BROKER]
        if self.MQTT_PORT in data:
            self._mqtt_port = data[self.MQTT_PORT]
        if self.MQTT_TOPIC in data:
            self._mqtt_topic = data[self.MQTT_TOPIC]
        self.notify_listeners(source)

    def to_dict(self) -> Dict:
        return {
            self.DO_MINE: self._do_mine,
            self.MQTT_BROKER: self._mqtt_broker,
            self.MQTT_PORT: self._mqtt_port,
            self.MQTT_TOPIC: self._mqtt_topic
        }

# Register with settings registry
SettingsRegistry.register("entropy", EntropySettings)

