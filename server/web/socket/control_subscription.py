import logging
from datetime import datetime
import json
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.devices.common.control_objects.control_object import ControlObject
from server.web.socket.base_websocket import BaseWebSocketClient
from server.tasks.control_device_task import ControlDeviceTask

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ControlSubscription(BaseWebSocketClient):
    """
    WebSocket client that handles control messages
    """

    def __init__(self, bb: BlackBoard, url: str):
        super().__init__(url, protocol="json")
        self.bb = bb

    def on_open(self, ws):
        """Called when the WebSocket connection is opened"""
        super().on_open(ws)
        # Send crypto state after connection init
        try:
            crypto_state = CryptoState()
            message = {
                "type": "crypto_state_update",
                "payload": crypto_state.to_dict()
            }
            self.send_message(message)
            logger.info("Sent initial crypto state")
        except Exception as e:
            logger.error(f"Error sending initial crypto state: {e}")

    def on_pong(self, ws, message):
        current_time = datetime.now().strftime('%H:%M:%S.%f')
        if hasattr(ws, 'last_ping_tm') and hasattr(ws, 'last_pong_tm'):
            ping_time = datetime.fromtimestamp(ws.last_ping_tm).strftime('%H:%M:%S.%f')
            pong_time = datetime.fromtimestamp(ws.last_pong_tm).strftime('%H:%M:%S.%f')
            diff = ws.last_pong_tm - ws.last_ping_tm
            logger.info("#" * 50)
            logger.info(f"Ping/Pong Details:")
            logger.info(f"Current time: {current_time}")
            logger.info(f"Last ping sent at: {ping_time}")
            logger.info(f"Pong received at: {pong_time}")
            logger.info(f"Round trip time: {diff:.3f} seconds")
            logger.info("#" * 50)

    def on_message(self, ws, message):
        """Called when a message is received"""
        try:
            data = json.loads(message)
            logger.info("#" * 50)
            logger.info(json.dumps(data, indent=2))
            logger.info("#" * 50)

            # Extract payload and add SN to body level
            payload = data.get('payload', {})
            data['sn'] = payload.get('sn')  # Add SN at body level

            # Check if this is a modbus protocol message
            protocol = payload.get('protocol')
            if protocol == 'modbus':
                try:
                    control_obj = ControlObject(data)
                    logger.info(f"Control object created - SN: {control_obj.sn}, Execute at: {control_obj.execute_at}, Commands: {len(control_obj.commands)}")

                    ms_from_now = int(control_obj.execute_at.timestamp() * 1000 - self.bb.time_ms())
                    logger.info(f"Time from now: {ms_from_now} ms")

                    self.bb.add_task(ControlDeviceTask(self.bb.time_ms() + ms_from_now, self.bb, control_obj))

                except Exception as e:
                    logger.error(f"Error creating control object: {e}")
                    error_message = {
                        "payload": {
                            "message": f"Failed to create control object: {str(e)}"
                        }
                    }
                    self.send_message(error_message)
            elif protocol:  # If protocol exists but is not modbus
                logger.warning(f"Unsupported protocol {protocol} in control message")
                error_message = {
                    "payload": {
                        "message": f"Unsupported protocol: {protocol}"
                    }
                }
                self.send_message(error_message)

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message received: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {message} error: {e}")
