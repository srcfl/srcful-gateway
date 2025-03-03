import logging
import time
from server.network.wifi import WiFiHandler, is_connected, get_ip_address
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
        self.connectivity_timeout = 30  # seconds
        log.debug("Initialized OpenWiFiConTask for SSID: %s with %d retries", 
                 self.wificon.ssid, self.retries)

    def _wait_for_network(self, timeout: int) -> bool:
        """Wait for network to be fully configured with timeout."""
        log.debug("Starting network wait sequence with %d seconds timeout", timeout)
        start_time = time.time()
        attempt = 1
        
        while time.time() - start_time < timeout:
            log.debug("Network check attempt %d", attempt)
            
            if not is_connected():
                log.debug("Network Manager reports no connection, waiting...")
                time.sleep(1)
                attempt += 1
                continue

            ip = get_ip_address()
            if ip == '0.0.0.0':
                log.debug("Invalid IP address (0.0.0.0), waiting...")
                time.sleep(1)
                attempt += 1
                continue

            log.debug("Network is fully configured and operational")
            return True

            time.sleep(1)
            attempt += 1
            
        log.warning("Network wait sequence timed out after %d seconds", timeout)
        return False

    def execute(self, event_time):
        log.info("Starting WiFi connection process to %s", self.wificon.ssid)
        try:
            if self.wificon.connect():
                log.debug("Initial WiFi connection successful, waiting for network configuration...")
                if self._wait_for_network(self.connectivity_timeout):
                    self.bb.add_info(f"Connected to WiFi: {self.wificon.ssid}")
                    
                    # Restart websocket connection
                    log.debug("Restarting WebSocket connection...")
                    from server.web.socket.settings_subscription import GraphQLSubscriptionClient
                    subscription = GraphQLSubscriptionClient.getInstance(self.bb, self.bb.settings.api.ws_endpoint)
                    subscription.restart_async()
                    
                    return None
                else:
                    log.warning("Network configuration failed after successful WiFi connection")
                    self.bb.add_warning("Connected to WiFi but no internet access")
                    if self.retries > 0:
                        self.retries -= 1
                        log.debug("Scheduling retry (%d remaining) in 10 seconds", self.retries)
                        self.time = event_time + 10000
                        return self
            else:
                log.warning("WiFi connection failed, possibly due to invalid credentials")
                self.bb.add_warning(f"Failed to connect to WiFi: {self.wificon.ssid}. Could be an invalid password.")
            return None
        except Exception as e:
            log.exception("Unexpected error during WiFi connection process")
            self.retries -= 1
            if self.retries > 0:    
                log.debug("Scheduling retry (%d remaining) in 10 seconds", self.retries)
                self.bb.add_error(f"Failed to connect to WiFi: {self.wificon.ssid}. Retry in 10 seconds")
                self.time = event_time + 10000
                return self
            else:
                log.error("All retries exhausted, giving up")
                self.bb.add_error(f"Failed to connect to WiFi: {self.wificon.ssid}. Giving up")
                return None

