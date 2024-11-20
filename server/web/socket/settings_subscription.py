import threading
import time
import logging
from websocket import WebSocketApp
import json
from server.app.blackboard import BlackBoard
import server.crypto.crypto as crypto
import signal
from typing import Callable
from datetime import datetime, timezone
from server.app.settings.settings import Settings
from server.app.settings.settings_observable import ChangeSource
from server.tasks.getSettingsTask import handle_settings
from server.tasks.requestResponseTask import handle_request_task, RequestTask


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class GraphQLSubscriptionClient(threading.Thread):
    def __init__(self, bb: BlackBoard, url: str):
        super().__init__()
        self.bb = bb
        self.url = url
        self.ws = None
        self.stop_event = threading.Event()
        self.headers = {
            "Sec-WebSocket-Protocol": "graphql-ws",
        }

    def run(self):
        while not self.stop_event.is_set():
            try:
                logger.info(f"Attempting to connect to WebSocket at {self.url}")
                self.ws = WebSocketApp(
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
                self.ws.run_forever(ping_interval=45)
            except Exception as e:
                logger.error(f"WebSocket error: {e} url: {self.url}")
            
            if not self.stop_event.is_set():
                logger.info("Reconnecting in 5 seconds...")
                time.sleep(5)

    def stop(self):
        self.stop_event.set()
        if self.ws:
            self.ws.close()

    def on_open(self, ws):
        logger.info("WebSocket connection opened")
        self.send_connection_init()

    def on_ping(self, ws, message):
        logger.debug(f"Received ping: {message}")
    def on_pong(self, ws, message):
        logger.debug(f"Received pong: {message}")

    def on_message(self, ws, message):
        logger.debug("Received message: %s", message)
        
        data = json.loads(message)

        if data.get('type') == 'connection_ack':
            logger.info("Connection acknowledged, sending subscription")
            self.subscribe_to_settings()
        elif data.get('type') == 'data':
            # This is what we should do next
            if 'data' in data['payload'] and 'configurationDataChanges' in data['payload']['data']:
                if data['payload']['data']['configurationDataChanges']['subKey'] == self.bb.settings.API_SUBKEY:
                    handle_settings(self.bb, data['payload']['data']['configurationDataChanges'])
                if data['payload']['data']['configurationDataChanges']['subKey'] == RequestTask.SUBKEY:
                    task = handle_request_task(self.bb, data['payload']['data']['configurationDataChanges'])
                    self.bb.add_task(task)
            

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
        logger.info(f"socked timeout: {self.ws.sock.gettimeout()}")


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