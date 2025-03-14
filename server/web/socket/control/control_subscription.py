import threading
import time
import logging
from websocket import WebSocketApp
import json
from server.app.blackboard import BlackBoard
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CustomWebSocketApp(WebSocketApp):
    """
    Custom WebSocketApp that handles pings and pongs with the case where the server sends unsolicited pongs and we need to reset the pong timer
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
                except Exception as e:
                    logger.debug(f"Failed to send ping: {e}")

    def _callback(self, callback, *args):
        if callback == self.on_pong:
            if self.expected_pongs > 0:
                # This is a response to our ping
                self.expected_pongs -= 1
                self.last_valid_pong_tm = time.time()
                super()._callback(callback, *args)
            else:
                # This is an unsolicited pong, reset the pong timer so we dont time out
                logger.debug("Received unsolicited pong, resetting pong timer")
                self.last_pong_tm = self.last_valid_pong_tm
                return
        else:
            super()._callback(callback, *args)


class ControlSubscription(threading.Thread):
    """
    A simple WebSocket client that handles basic socket communication with custom message formats
    """

    def __init__(self, bb: BlackBoard, url: str):
        super().__init__()
        self.bb = bb
        self.url = url
        self.ws: Optional[WebSocketApp] = None
        self.stop_event = threading.Event()
        self.PING_INTERVAL = 45  # seconds

    def run(self):
        while not self.stop_event.is_set():
            try:
                logger.info(f"Attempting to connect to WebSocket at {self.url} from ControlSubscription")
                headers = {
                    "User-Agent": "Python/WebSocket-Client",
                    "Sec-WebSocket-Protocol": "json"  # Add this to indicate we're using JSON protocol
                }
                self.ws = CustomWebSocketApp(
                    self.url,
                    header=headers,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_ping=self.on_ping,
                    on_pong=self.on_pong,
                )

                logger.info(f"WebSocket connection opened")
                self.ws.run_forever(ping_interval=self.PING_INTERVAL, ping_timeout=10)
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

    def send_message(self, message: dict):
        """Send a message through the WebSocket"""
        if self.ws and self.ws.sock:
            try:
                self.ws.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message: {e}")

    def on_open(self, ws):
        """Called when the WebSocket connection is opened"""
        logger.info("WebSocket connection opened")
        # Send connection initialization message
        init_message = {
            "type": "connection_init",
            "payload": {}
        }
        self.send_message(init_message)
        logger.info("Sent connection_init message")

    def on_ping(self, ws, message):
        logger.debug(f"Received ping: {message}")

    def on_pong(self, ws, message):
        formatted_time = datetime.fromtimestamp(ws.last_ping_tm).strftime('%H:%M:%S.%f')
        logger.debug(f"Received ping at {formatted_time}: {repr(message)}")
        formatted_time = datetime.fromtimestamp(ws.last_pong_tm).strftime('%H:%M:%S.%f')
        logger.debug(f"Received pong at {formatted_time}: {repr(message)}")
        diff = ws.last_pong_tm - ws.last_ping_tm
        logger.debug(f"Ping/pong difference: {diff} seconds")

    def on_message(self, ws, message):
        """Called when a message is received"""
        logger.debug("Received message: %s", message)
        try:
            data = json.loads(message)
            message_type = data.get('type')
            logger.info(f"Received message type: {message_type}")

            if message_type == 'connection_ack':
                logger.info("Connection acknowledged")
            else:
                # Process your custom message format here
                logger.info(f"Processed message: {data}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message received: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {message} error: {e}")

    def on_error(self, ws, error):
        """Called when a WebSocket error occurs"""
        logger.error(f"WebSocket error: {error}, url: {self.url}")

    def on_close(self, ws, close_status_code, close_msg):
        """Called when the WebSocket connection is closed"""
        logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
