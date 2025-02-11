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
        self.scanning = False

    def execute(self, event_time):
        

        if self.retries <= 0:
            logger.error("No more retries left for scanning WiFi networks")
            return None

        if self.scanning:
            # check if we got a result
            s = WifiScanner()
            ssids = s.get_ssids()
            if ssids:
                logger.info("WiFi scan got some results, scheduling state save in 2 seconds")
                self.retries -= 1
                if self.retries <= 0:
                    logger.error("No more retries left for scanning WiFi networks")
                    return SaveStateTask(self.bb.time_ms() + 1000 * 2, self.bb)
                                         
                self.adjust_time(self.bb.time_ms() + 1000 * 10)
                return [self, SaveStateTask(self.bb.time_ms() + 1000 * 2, self.bb)]
            else:
                self.scanning = False
                logger.info("Retrying wifi scan in 30 seconds")
                self.adjust_time(self.bb.time_ms() + 1000 * 30)
                self.retries -= 1
                if self.retries <= 0:
                    logger.error("No more retries left for scanning WiFi networks")
                    return None
                return self
            
        try:
            logger.info("Initiating scan for WiFi networks")
            s = WifiScanner()
            s.scan()
            self.scanning = True
            self.adjust_time(self.bb.time_ms() + 1000 * 10)
            return self
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
