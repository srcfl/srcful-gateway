import logging

from server.wifi.scan import WifiScanner
from server.blackboard import BlackBoard

from .task import Task


log = logging.getLogger(__name__)


class ScanWiFiTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        self.retries = 3

    def execute(self, event_time):
        log.info("Scanning for WiFi networks")
        try:
            s = WifiScanner()
            s.scan()
            return None
        except Exception as e:
            log.Error("Failed to scan for WiFi networks")
            log.exception(e)
            self.retries -= 1
            if self.retries <= 0:
                log.error("No more retries left for scanning WiFi networks")
                return None

            log.info("Retrying wifi scan in 30 seconds")
            self.time = event_time + 30000
            return self
