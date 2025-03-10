import logging
from datetime import datetime, UTC
import json
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.web.socket.control.control_messages.base_message import BaseMessage
from server.web.socket.control.control_messages.control_message import ControlMessage
from server.web.socket.control.control_messages.auth_challenge_message import AuthChallengeMessage
from server.web.socket.base_websocket import BaseWebSocketClient
from server.web.socket.control.control_messages.types import ControlMessageType, PayloadType
from server.crypto import crypto
from cryptography.hazmat.primitives import hashes
from server.tasks.control_device_task import ControlDeviceTask, ControlDeviceTaskListener
from typing import Any, List
from server.web.socket.control.task_execution_registry import TaskExecutionRegistry


DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
TRUSTED_PUBLIC_KEY = "245bbc0a266ebfecc24983561f9cb37d5ff9844cb95669bdd8019ad5a00177f361878a047e0d8c4c5cccd7c7529873ebfabd0a76f9cda60c0e4bd7e1b924a8ff"  # Temporary public key for testing

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ControlSubscription(BaseWebSocketClient, ControlDeviceTaskListener):
    """
    WebSocket client that handles control messages
    """

    def __init__(self, bb: BlackBoard, url: str):
        super().__init__(url, protocol="json")
        self.bb: BlackBoard = bb
        self.crypto_state: CryptoState = CryptoState()
        self.task_registry = TaskExecutionRegistry()

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
            # logger.info(f"Signature: {signature}")
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
        logger.info(f"Sending ACK for message: {message.id}, Type: {message.type}, signature: {message.signature}")
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
        logger.info(f"Sending NACK for message: {message.id}, Type: {message.type}, signature: {message.signature}")
        self.send_message(nack_data)

    def on_control_device_task_started(self, task: ControlDeviceTask):
        pass

    def on_control_device_task_completed(self, task: ControlDeviceTask):
        # If task is executed, send an ACK and update the task registry, else send a NACK
        if task.is_executed:
            # self._send_ack(task.control_message)
            task.is_acked = True
            self.task_registry.register_task_result(task)
        else:
            self._send_nack(task.control_message, "Task not executed")
            task.is_nacked = True

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
                self._send_nack(message_object, "Invalid signature")
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

            logger.info("*" * 50)
            logger.info("Task execution registry:")
            for task in self.task_registry.get_all_results():
                logger.info(f"Task: {task.control_message.id}, Scheduled at: {task.control_message.execute_at}, Is executed: {task.is_executed}, Executed at: {datetime.fromtimestamp(task.executed_at_timestamp / 1000)}, Is acked: {task.is_acked}, Is nacked: {task.is_nacked}")
            logger.info("*" * 50)

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message received: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {message} error: {e}")

    def handle_ems_authentication_success(self, data: dict):
        base_message: BaseMessage = BaseMessage(data)
        pass

    def handle_ems_authentication_error(self, data: dict):
        pass

    def handle_device_authenticate(self, data: dict):

        auth_challenge_message: AuthChallengeMessage = AuthChallengeMessage(data)
        # self._send_ack(auth_challenge_message)

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

        # logger.info("#*" * 50)
        # logger.info(json.dumps(ret_data))
        # logger.info("#*" * 50)

        self.send_message(ret_data)

    def handle_ems_control_schedule(self, data: dict):

        control_message: ControlMessage = ControlMessage(data)

        self._send_ack(control_message)

        der = self.bb.devices.find_sn(control_message.sn)

        if not der:
            self._send_nack(control_message, "Device not found")
            logger.error(f"Device not found: {control_message.sn}")
            return

        logger.info(f"Device found: {der.get_name()}")

        # Convert execute_at to milliseconds since epoch
        time_now_ms: int = int(datetime.now().timestamp() * 1000)

        execute_at_ms: int = int(datetime.strptime(control_message.execute_at, DATE_TIME_FORMAT).timestamp() * 1000)

        # print the ETA in a human readable format, e.g. "ETA: 1:30:10"
        eta: datetime = datetime.fromtimestamp(execute_at_ms / 1000) - datetime.now()
        logger.info(f"ETA: {eta}, or {execute_at_ms - time_now_ms} milliseconds")

        if self.task_registry.get_task_result(control_message.id):
            logger.info(f"Task already exists in registry, skipping")
            return

        task = ControlDeviceTask(execute_at_ms, self.bb, control_message)
        task.register_listener(self)

        self.bb.add_task(task)
