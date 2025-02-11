import logging
import time
from server.network.wifi import WiFiHandler
from server.app.blackboard import BlackBoard
from server.tasks.saveStateTask import SaveStateTask
from server.tasks.scanWiFiTask import ScanWiFiTask

from .task import Task


log = logging.getLogger(__name__)


class OpenWiFiConTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, wificon: WiFiHandler):
        super().__init__(event_time, bb)
        self.wificon = wificon
        self.retries = 3

    def execute(self, event_time):
        log.info("Opening WiFi connection to %s", self.wificon.ssid)
        try:
            if self.wificon.connect():
                self.bb.add_info(f"Connected to WiFi: {self.wificon.ssid}")
                # adding a notification saves the state - hopefully this will catch the new ssid

                # we now need to restart the websocket connection
                from server.web.socket.settings_subscription import GraphQLSubscriptionClient
                subscription = GraphQLSubscriptionClient.getInstance(self.bb, self.bb.settings.api.ws_endpoint)
                subscription.restart_async()

                return None
            else:
                self.bb.add_warning(f"Failed to connect to WiFi: {self.wificon.ssid}. Could be an invalid password.")
            return None
        except Exception as e:
            log.exception(e)
            self.retries -= 1
            if self.retries > 0:    
                self.bb.add_error(f"Failed to connect to WiFi: {self.wificon.ssid}. Retry in 10 seconds")
                self.time = event_time + 10000
                return self
            else:
                self.bb.add_error(f"Failed to connect to WiFi: {self.wificon.ssid}. Giving up")
                return None

