import logging
from datetime import datetime
import json
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.devices.common.control_objects.control_object import ControlObject
from server.web.socket.base_websocket import BaseWebSocketClient
from server.tasks.control_device_task import ControlDeviceTask
from .types import ControlMessageType, PayloadType
from server.crypto import crypto


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ControlSubscription(BaseWebSocketClient):
    """
    WebSocket client that handles control messages
    """

    def __init__(self, bb: BlackBoard, url: str):
        super().__init__(url, protocol="json")
        self.bb: BlackBoard = bb
        self.crypto_state: CryptoState = CryptoState()

    def on_open(self, ws):
        """Called when the WebSocket connection is opened"""
        super().on_open(ws)

    def on_pong(self, ws, message):
        current_time = datetime.now().strftime('%H:%M:%S.%f')
        if hasattr(ws, 'last_ping_tm') and hasattr(ws, 'last_pong_tm'):
            ping_time = datetime.fromtimestamp(ws.last_ping_tm).strftime('%H:%M:%S.%f')
            pong_time = datetime.fromtimestamp(ws.last_pong_tm).strftime('%H:%M:%S.%f')
            diff = ws.last_pong_tm - ws.last_ping_tm
            logger.info("#" * 50)
            logger.info(f"Ping/Pong Details - Current: {current_time}, Ping: {ping_time}, Pong: {pong_time}, RTT: {diff:.3f}s")
            logger.info("#" * 50)

    def on_message(self, ws, message):
        """Called when a message is received"""
        try:
            data = json.loads(message)
            logger.info("#" * 50)
            logger.info(json.dumps(data, indent=2))
            logger.info("#" * 50)

            type: str = data.get(PayloadType.TYPE, None)

            if type == ControlMessageType.EMS_AUTHENTICATION_SUCCESS:
                self.handle_ems_authentication_success(data)

            elif type == ControlMessageType.EMS_AUTHENTICATION_ERROR:
                self.handle_ems_authentication_error(data)

            elif type == ControlMessageType.EMS_AUTHENTICATION_CHALLENGE:
                self.handle_device_authenticate(data)

            elif type == ControlMessageType.EMS_CONTROL_SCHEDULE:
                self.handle_ems_control_schedule(data)

            else:
                logger.warning(f"Unknown message type: {type}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message received: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {message} error: {e}")

    def handle_ems_authentication_success(self, data: dict):
        """Handle ems authentication success"""
        logger.info("Received EMS authentication success")

    def handle_ems_authentication_error(self, data: dict):
        """Handle ems authentication error"""
        logger.info("Received EMS authentication error")

    def handle_device_authenticate(self, data: dict):
        """Handle device authenticate"""
        logger.info("Received EMS authentication challenge")

        timestamp: str = datetime.now().isoformat()
        serial_number: str = "01239d34ba0bb9a601"
        combined_data: str = f"{serial_number}.{timestamp}"

        with crypto.Chip() as chip:
            signature = chip.get_signature(combined_data).hex()
            logger.info(f"Signature: {signature}")

            data = {
                PayloadType.TYPE: ControlMessageType.DEVICE_AUTHENTICATE,
                PayloadType.PAYLOAD: {
                    PayloadType.DEVICE_NAME: self.crypto_state.serial_number.hex(),
                    PayloadType.SERIAL_NUMBER: serial_number,
                    PayloadType.SIGNATURE: signature,
                    PayloadType.CREATED_AT: timestamp
                }
            }
            self.send_message(data)

    def handle_ems_control_schedule(self, data: dict):
        """Handle ems control schedule"""
        logger.info("Received EMS control schedule")
