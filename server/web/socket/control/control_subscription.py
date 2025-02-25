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
from server.tasks.control_device_task import ControlDeviceTask


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
        crypto_sn: str = self.crypto_state.serial_number.hex()
        data_to_sign: str = f"{crypto_sn}:{timestamp}"

        with crypto.Chip() as chip:
            signature = chip.get_signature(data_to_sign).hex()
            logger.info(f"Signature: {signature}")
            return timestamp, crypto_sn, signature

        return None

    # TODO: Write tests for this!
    def _send_ack(self, message: BaseMessage):
        timestamp, serial_number, signature = self._create_signature()

        ack_data = {
            PayloadType.TYPE: ControlMessageType.DEVICE_CONTROL_SCHEDULE_ACK,
            PayloadType.PAYLOAD: {
                PayloadType.ID: message.id,
                PayloadType.SERIAL_NUMBER: serial_number,
                PayloadType.SIGNATURE: signature,
                PayloadType.CREATED_AT: timestamp
            }
        }
        logger.info(f"Sending ACK: {ack_data}")
        self.send_message(ack_data)

    # TODO: Write tests for this!
    def _send_nack(self, message: BaseMessage, reason: str):
        timestamp, serial_number, signature = self._create_signature()

        nack_data = {
            PayloadType.TYPE: ControlMessageType.DEVICE_CONTROL_SCHEDULE_NACK,
            PayloadType.PAYLOAD: {
                PayloadType.ID: message.id,
                PayloadType.REASON: reason,
                PayloadType.SERIAL_NUMBER: serial_number,
                PayloadType.SIGNATURE: signature,
                PayloadType.CREATED_AT: timestamp
            }
        }
        logger.info(f"Sending NACK: {nack_data}")
        self.send_message(nack_data)

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
        timestamp, crypto_sn, signature = self._create_signature()

        ret_data = {
            PayloadType.TYPE: ControlMessageType.DEVICE_AUTHENTICATE,
            PayloadType.PAYLOAD: {
                PayloadType.DEVICE_NAME: self.crypto_state.device_name,
                PayloadType.SERIAL_NUMBER: crypto_sn,
                PayloadType.SIGNATURE: signature,
                PayloadType.CREATED_AT: timestamp
            }
        }
        self.send_message(ret_data)

    def handle_ems_control_schedule(self, data: dict):

        control_object: ControlMessage = ControlMessage(data)

        flag = True

        if flag:
            self._send_ack(control_object)
        else:
            self._send_nack(control_object, "Just a very long reason to write here")

        der = self.bb.devices.find_sn(control_object.sn)

        if not der:
            self._send_nack(control_object, "Device not found")
            logger.error(f"Device not found: {control_object.sn}")
            return

        logger.info(f"Device found: {der.get_name()}")

        # Convert execute_at to milliseconds since epoch
        time_now_ms: int = int(datetime.now().timestamp() * 1000)
        # convert time string to datetime object
        execute_at_ms: int = int(datetime.strptime(control_object.execute_at, DATE_TIME_FORMAT).timestamp() * 1000)

        # print the ETA in a human readable format, e.g. "ETA: 1:30:10"
        eta: datetime = datetime.fromtimestamp(execute_at_ms / 1000) - datetime.now()

        execute_in_ms: int = execute_at_ms - time_now_ms

        logger.info(f"ETA: {eta}, or {execute_in_ms} milliseconds")

        task = ControlDeviceTask(execute_in_ms, self.bb, control_object)
        self.bb.add_task(task)
