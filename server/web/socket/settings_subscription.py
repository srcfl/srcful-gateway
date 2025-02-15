import threading
import time
import logging
from websocket import WebSocketApp
import json
from server.app.blackboard import BlackBoard
import server.crypto.crypto as crypto
from typing import Callable
from datetime import datetime, timezone
from server.tasks.getSettingsTask import handle_settings
from server.tasks.requestResponseTask import handle_request_task, RequestTask


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


class GraphQLSubscriptionClient(threading.Thread):

    _instances = {}  # Class variable to store instances
    _instances_lock = threading.Lock()  # Thread-safe instance creation

    @classmethod
    def getInstance(cls, bb: BlackBoard, url: str) -> 'GraphQLSubscriptionClient':
        with cls._instances_lock:
            if url not in cls._instances:
                instance = cls(bb, url)
            return cls._instances[url]

    @classmethod
    def removeInstance(cls, url: str):
        with cls._instances_lock:
            if url in cls._instances:
                del cls._instances[url]

    def __init__(self, bb: BlackBoard, url: str):
        if url in self._instances:
            raise RuntimeError(f"Instance for URL {url} already exists. Use getInstance() instead")
        super().__init__()
        self.bb = bb
        self.url = url
        self.ws = None
        self.stop_event = threading.Event()
        self.headers = {
            "Sec-WebSocket-Protocol": "graphql-ws",
        }
        self.PING_INTERVAL = 45  # seconds
        self._instances[url] = self

    def run(self):

        while not self.stop_event.is_set():
            try:
                logger.info(f"Attempting to connect to WebSocket at {self.url}")
                self.ws = CustomWebSocketApp(
                    self.url,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_ping=self.on_ping,
                    on_pong=self.on_pong,
                    header=self.headers
                )

                logger.info(f"WebSocket connection opened")
                self.ws.run_forever(ping_interval=self.PING_INTERVAL, ping_timeout=10)
            except Exception as e:
                logger.error(f"WebSocket error: {e} url: {self.url}")

            if not self.stop_event.is_set():
                logger.info("Reconnecting in 5 seconds...")
                time.sleep(5)

    def stop(self):
        self.stop_event.set()
        if self.ws:
            self.ws.close()

    def restart_async(self):
        """Asynchronously restart this client instance"""
        def _restart_thread():
            logger.info(f"Starting async restart for {self.url}")
            self.restart()

        restart_thread = threading.Thread(target=_restart_thread)
        restart_thread.daemon = True  # Make it a daemon thread so it won't prevent program exit
        restart_thread.start()

    def restart(self):
        """Restarts the client thread and connection. Note that this creates a new instance and the old instance will be dead"""

        url = self.url  # Store URL before removing instance
        bb = self.bb    # Store blackboard before removing instance

        logger.info(f"Restarting WebSocket client for {self.url}")
        # First stop everything
        self.stop_event.set()
        if self.ws:
            self.ws.close()

        try:
            self.join(timeout=3*self.PING_INTERVAL)
        except threading.TimeoutError:
            logger.error("Thread join timed out during restart - thread might not have cleaned up properly")

        # Remove this instance
        GraphQLSubscriptionClient.removeInstance(url)

        # Create and start new instance
        GraphQLSubscriptionClient.getInstance(bb, url).start()

    def on_open(self, ws):
        logger.info("WebSocket connection opened")
        self.send_connection_init()

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
        logger.debug("Received message: %s", message)
        try:
            data = json.loads(message)

            if data and isinstance(data, dict):
                if data.get('type') == 'connection_ack':
                    logger.info("Connection acknowledged, sending subscription")
                    self.subscribe_to_settings()
                elif data.get('type') == 'data':
                    # This is what we should do next
                    if 'data' in data['payload'] and 'configurationDataChanges' in data['payload']['data']:
                        if data['payload']['data']['configurationDataChanges']['subKey'] == self.bb.settings.SETTINGS_SUBKEY:
                            handle_settings(self.bb, data['payload']['data']['configurationDataChanges'])
                        if data['payload']['data']['configurationDataChanges']['subKey'] == RequestTask.SUBKEY:
                            task = handle_request_task(self.bb, data['payload']['data']['configurationDataChanges'])
                            self.bb.add_task(task)
            else:
                logger.error(f"Invalid message: {message}")
        except json.JSONDecodeError:
            logger.error(f"Invalid message: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {message} error: {e}")
            if message is not None:
                data = json.loads(message)
                if data.get('type') == 'data' and data.get('payload').get('errors'):
                    logger.info("Error received, reconnecting")
                    self.send_connection_init()
            return

    def on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}, url: {self.url}")

    def on_close(self, ws, close_status_code, close_msg):
        logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")

    def send_connection_init(self):
        init_message = {
            "type": "connection_init",
            "payload": {}
        }
        self.ws.send(json.dumps(init_message))
        logger.info("Sent connection_init message")
        logger.debug(f"socked timeout: {self.ws.sock.gettimeout()}")

    def _get_subscription_query(self, chip_constructor: Callable[[], crypto.Chip]):
        query = """
        subscription {
          configurationDataChanges(deviceAuth: {
            id: "$serial",
            timestamp: "$timestamp",
            signedIdAndTimestamp: "$signature",
          }) {
            data
            subKey
          }
        }
        """

        # Convert Unix timestamp to datetime object
        unix_timestamp = int(time.time())
        dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)

        # Format datetime as ISO 8601 string
        # should be something like 2024-08-26T13:02:00
        iso_timestamp = dt.isoformat().replace('+00:00', '')

        with chip_constructor() as chip:
            serial = chip.get_serial_number().hex()
            timestamp = iso_timestamp
            message = f"{serial}:{timestamp}"
            signature = chip.get_signature(message).hex()

        query = query.replace("$serial", serial)
        query = query.replace("$timestamp", timestamp)
        query = query.replace("$signature", signature)

        return query

    def subscribe_to_settings(self):

        query = self._get_subscription_query(crypto.Chip)

        subscription_message = {
            "type": "start",
            "id": "1",
            "payload": {
                "query": query
            }
        }

        self.ws.send(json.dumps(subscription_message))
