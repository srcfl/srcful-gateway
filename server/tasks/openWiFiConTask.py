import logging
from server.network.wifi import WiFiHandler
from server.app.blackboard import BlackBoard
from server.tasks.scanWiFiTask import ScanWiFiTask

from .task import Task


log = logging.getLogger(__name__)


class OpenWiFiConTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, wificon: WiFiHandler):
        super().__init__(event_time, bb)
        self.wificon = wificon

    def execute(self, event_time):
        log.info("Opening WiFi connection to %s", self.wificon.ssid)
        try:
            self.wificon.connect()
            self.bb.add_task(ScanWiFiTask(self.bb.time_ms() + 1000, self.bb))
            return None
        except Exception as e:
            self.bb.notify_error("Failed to connect to WiFi. Invalid SSID or PSK: ")
            log.exception(e)
            self.time = event_time + 10000
            return self
