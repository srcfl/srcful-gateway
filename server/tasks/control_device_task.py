import logging
from server.app.blackboard import BlackBoard
from .task import Task
from server.web.socket.control.control_messages.control_message import ControlMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ControlDeviceTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, control_message: ControlMessage):
        super().__init__(event_time, bb)
        self.control_message = control_message
        self.is_cancelled = False

        logger.info(f"Control device task with id {self.control_message.id} initialized and will execute at {self.time}")

    def execute(self, event_time) -> list[bool]:

        if not self.is_cancelled:
            der_sn = self.control_message.sn
            device = self.bb.devices.find_sn(der_sn)

            if device is None:
                logger.error(f"Device not found: {der_sn}")
                return None

            logger.info(f"Executing control object with id: {self.control_message.id}, message: {self.control_message}")

            # Execute the control message and return its results
            # The observer pattern is now handled by the TaskExecutor
            return self.control_message.execute(device)

        return None
