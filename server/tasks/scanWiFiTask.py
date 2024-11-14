import logging
from server.network.scan import WifiScanner
from server.app.blackboard import BlackBoard
from server.tasks.saveStateTask import SaveStateTask
from .task import Task


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ScanWiFiTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        self.retries = 3

    def execute(self, event_time):
        logger.info("Scanning for WiFi networks")
        try:
            s = WifiScanner()
            s.scan()
            return SaveStateTask(event_time + 1000 * 30, self.bb)
        except Exception as e:
            logger.error("Failed to scan for WiFi networks")
            logger.exception(e)
            self.retries -= 1
            if self.retries <= 0:
                logger.error("No more retries left for scanning WiFi networks")
                return None

            logger.info("Retrying wifi scan in 30 seconds")
            self.time = event_time + 30000
            return self
