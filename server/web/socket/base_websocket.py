import threading
import time
import logging
from websocket import WebSocketApp
import json
from typing import Optional, Dict, Any
from datetime import datetime


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseWebSocketApp(WebSocketApp):
    """
    Base WebSocket app that handles pings and pongs with the case where the server sends unsolicited pongs
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_pongs = 0
        self.last_valid_pong_tm = 0

    def _send_ping(self) -> None:
        if self.stop_ping.wait(self.ping_interval) or self.keep_running is False:
            return

        while not self.stop_ping.wait(self.ping_interval) and self.keep_running is True:
            if self.sock:

                try:
                    logger.debug("Sending ping")
                    self.sock.ping(self.ping_payload)
                    self.last_ping_tm = time.time()
                    self.expected_pongs += 1
                    logger.debug(f"Expected pongs: {self.expected_pongs}")
                except Exception as e:
                    logger.error(f"Failed to send ping: {e}")

    def _callback(self, callback, *args):
        if callback == self.on_pong:
            if self.expected_pongs > 0:
                # This is a response to our ping
                self.expected_pongs -= 1
                self.last_valid_pong_tm = time.time()
                logger.debug(f"Remaining expected pongs: {self.expected_pongs}")
                super()._callback(callback, *args)
            else:
                # This is an unsolicited pong, reset the pong timer so we dont time out
                logger.debug("Received unsolicited pong, resetting pong timer")
                self.last_pong_tm = self.last_valid_pong_tm
                return
        else:
            super()._callback(callback, *args)


class BaseWebSocketClient(threading.Thread):
    """
    Base WebSocket client that handles basic socket communication
    """

    def __init__(self, url: str, protocol: str = "json"):
        super().__init__()
        self.url = url
        self.ws: Optional[BaseWebSocketApp] = None
        self.stop_event = threading.Event()
        self.PING_INTERVAL = 60  # seconds
        self.PING_TIMEOUT = 30  # seconds
        self.headers = {
            # "User-Agent": "Python/WebSocket-Client",
            "Sec-WebSocket-Protocol": protocol
        }

        self.connection_start_time = None
        self.reconnect_count = 0
        self.last_error_time = None

    def run(self):
        while not self.stop_event.is_set():
            try:
                logger.info(f"Connecting to WebSocket at {self.url}")
                self.ws = BaseWebSocketApp(
                    self.url,
                    header=self.headers,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_ping=self.on_ping,
                    on_pong=self.on_pong
                )
                self.ws.run_forever(ping_interval=self.PING_INTERVAL, ping_timeout=self.PING_TIMEOUT)
                self.connected = False
            except Exception as e:
                logger.error(f"WebSocket error: {e} url: {self.url}")

            if not self.stop_event.is_set():
                logger.info("Reconnecting in 5 seconds...")
                time.sleep(5)

    def stop(self):
        """Stop the WebSocket client"""
        self.stop_event.set()
        if self.ws:
            self.ws.close()

    def send_message(self, message: Dict[str, Any]) -> None:
        """Send a message through the WebSocket"""
        if self.ws and self.ws.sock:
            try:
                if isinstance(message, (dict, list)):
                    self.ws.send(json.dumps(message))
                else:
                    self.ws.send(str(message))
            except Exception as e:
                logger.error(f"Error sending message: {e}")

    def on_open(self, ws):
        """Called when the WebSocket connection is opened"""
        self.connection_start_time = time.time()
        logger.info("WebSocket connection opened")
        if self.reconnect_count > 0:
            connection_gap = "unknown"
            if self.last_error_time:
                connection_gap = f"{time.time() - self.last_error_time:.2f} seconds"
            logger.info(f"Reconnected after {connection_gap} (attempt #{self.reconnect_count})")
        self.send_connection_init()

    def send_connection_init(self):
        """Send connection initialization message"""
        # TODO: Implement connection initialization message if needed, here or in a subclass
        pass

    def on_ping(self, ws, message):
        pass

    def on_pong(self, ws, message):
        pass

    def on_message(self, ws, message):
        """Called when a message is received"""
        # TODO: Implement message handling if needed, here or in a subclass
        pass

    def on_error(self, ws, error):
        """Called when a WebSocket error occurs"""
        self.last_error_time = time.time()

        error_type = type(error).__name__
        connection_duration = "unknown"
        if self.connection_start_time:
            connection_duration = f"{time.time() - self.connection_start_time:.2f} seconds"

        logger.error(f"WebSocket error: {error}, type: {error_type}, duration: {connection_duration}")

    def on_close(self, ws, close_status_code, close_msg):
        """Called when the WebSocket connection is closed"""
        connection_duration = "unknown"
        if self.connection_start_time:
            connection_duration = f"{time.time() - self.connection_start_time:.2f} seconds"

        logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}, duration: {connection_duration}")
        self.reconnect_count += 1
