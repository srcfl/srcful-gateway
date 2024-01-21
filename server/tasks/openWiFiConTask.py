from .task import Task
from server.wifi.wifi import WiFiHandler
from server.blackboard import BlackBoard


import logging

log = logging.getLogger(__name__)


class OpenWiFiConTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, wificon: WiFiHandler):
        super().__init__(event_time, bb)
        self.wificon = wificon

    def execute(self, event_time):
        log.info("Opening WiFi connection to {}".format(self.wificon.ssid))
        try:
            self.wificon.connect()
        except Exception as e:
            log.Error("Failed to connect to WiFi. Invalid SSID or PSK: ")
            log.exception(e)
            self.time = event_time + 10000
            return self
