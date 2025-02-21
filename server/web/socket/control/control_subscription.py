import logging
from datetime import datetime, UTC
import json
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.web.socket.control.control_objects.base_message import BaseMessage
from server.web.socket.control.control_objects.control_message import ControlMessage
from server.web.socket.control.control_objects.auth_challenge_message import AuthChallengeMessage
from server.web.socket.base_websocket import BaseWebSocketClient
from server.web.socket.control.control_objects.types import ControlMessageType, PayloadType
from server.crypto import crypto
from cryptography.hazmat.primitives import hashes

DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
TRUSTED_PUBLIC_KEY = "245bbc0a266ebfecc24983561f9cb37d5ff9844cb95669bdd8019ad5a00177f361878a047e0d8c4c5cccd7c7529873ebfabd0a76f9cda60c0e4bd7e1b924a8ff"  # Temporary public key for testing

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

    def _verify_message_signature(self, message: BaseMessage) -> bool:
        """Validate the signature of the message"""
        # The public key to verify against
        pub_key: bytes = bytes.fromhex(TRUSTED_PUBLIC_KEY)

        # The signature from the message
        signature: bytes = bytes.fromhex(message.signature)

        # The data that was signed: {serial_number}:{created_at}
        data: str = f"{message.serial_number}:{message.created_at}"

        # Hash the data before verifying
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data.encode())
        data_hash = digest.finalize()

        logger.info(f"Verifying signature for data: {data}")

        with crypto.Chip() as chip:
            return chip.verify_signature(
                data_hash=data_hash,
                signature=signature,
                public_key=pub_key
            )

    def _create_signature(self) -> tuple[str, str, str]:
        timestamp: str = datetime.now(UTC).strftime(DATE_TIME_FORMAT)
        serial_number: str = self.crypto_state.serial_number.hex()
        data_to_sign: str = f"{serial_number}:{timestamp}"

        with crypto.Chip() as chip:
            signature = chip.get_signature(data_to_sign).hex()
            logger.info(f"Signature: {signature}")
            return timestamp, serial_number, signature

        return None

    def on_open(self, ws):
        """Called when the WebSocket connection is opened"""
        super().on_open(ws)

    def on_pong(self, ws, message):
        current_time = datetime.now().strftime(DATE_TIME_FORMAT)
        if hasattr(ws, 'last_ping_tm') and hasattr(ws, 'last_pong_tm'):
            ping_time = datetime.fromtimestamp(ws.last_ping_tm).strftime(DATE_TIME_FORMAT)
            pong_time = datetime.fromtimestamp(ws.last_pong_tm).strftime(DATE_TIME_FORMAT)
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

            message_object: BaseMessage = BaseMessage(data)
            if not self._verify_message_signature(message_object):
                logger.error("Invalid signature")
                return

            type: str = data.get(PayloadType.TYPE, None)

            if type == ControlMessageType.EMS_AUTHENTICATION_SUCCESS:
                logger.info("Received EMS authentication success")
                self.handle_ems_authentication_success(data)

            elif type == ControlMessageType.EMS_AUTHENTICATION_ERROR:
                logger.info("Received EMS authentication error")
                self.handle_ems_authentication_error(data)

            elif type == ControlMessageType.EMS_AUTHENTICATION_CHALLENGE:
                logger.info("Received EMS authentication challenge")
                self.handle_device_authenticate(data)

            elif type == ControlMessageType.EMS_CONTROL_SCHEDULE:
                logger.info("Received EMS control schedule")
                self.handle_ems_control_schedule(data)

            else:
                logger.warning(f"Unknown message type: {type}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message received: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {message} error: {e}")

    def handle_ems_authentication_success(self, data: dict):
        pass

    def handle_ems_authentication_error(self, data: dict):
        pass

    def handle_device_authenticate(self, data: dict):

        auth_challenge_message: AuthChallengeMessage = AuthChallengeMessage(data)

        timestamp, serial_number, signature = self._create_signature()

        ret_data = {
            PayloadType.TYPE: ControlMessageType.DEVICE_AUTHENTICATE,
            PayloadType.PAYLOAD: {
                PayloadType.DEVICE_NAME: "Deye",
                PayloadType.SERIAL_NUMBER: serial_number,
                PayloadType.SIGNATURE: signature,
                PayloadType.CREATED_AT: timestamp
            }
        }
        self.send_message(ret_data)

    def handle_ems_control_schedule(self, data: dict):

        control_object: ControlMessage = ControlMessage(data)

        flag = True

        if flag:
            # TODO: Send ACK
            timestamp, serial_number, signature = self._create_signature()

            ack_data = {
                PayloadType.TYPE: ControlMessageType.DEVICE_CONTROL_SCHEDULE_ACK,
                PayloadType.PAYLOAD: {
                    PayloadType.ID: control_object.id,
                    PayloadType.SERIAL_NUMBER: serial_number,
                    PayloadType.SIGNATURE: signature,
                    PayloadType.CREATED_AT: timestamp
                }
            }
            self.send_message(ack_data)

        else:
            # TODO: Send NACK
            timestamp, serial_number, signature = self._create_signature()

            nack_data = {
                PayloadType.TYPE: ControlMessageType.DEVICE_CONTROL_SCHEDULE_NACK,
                PayloadType.PAYLOAD: {
                    PayloadType.ID: control_object.id,
                    PayloadType.REASON: "Just a very long reason to write here",
                    PayloadType.SERIAL_NUMBER: serial_number,
                    PayloadType.SIGNATURE: signature,
                    PayloadType.CREATED_AT: timestamp
                }
            }
            self.send_message(nack_data)
