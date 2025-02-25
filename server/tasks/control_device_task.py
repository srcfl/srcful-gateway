import logging
from server.app.blackboard import BlackBoard
from .task import Task
from server.web.socket.control.control_objects.control_message import ControlMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ControlDeviceTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, control_object: ControlMessage):
        super().__init__(event_time, bb)
        self.control_object = control_object

        logger.info(f"Control device task with id {self.control_object.id} initialized and will execute in {self.time} milliseconds...")

    def execute(self, event_time) -> None | Task | list[Task]:
        der_sn = self.control_object.sn
        device = self.bb.devices.find_sn(der_sn)

        if device is None:
            logger.error(f"Device not found: {der_sn}")
            return None

        logger.info(f"Executing control object with id: {self.control_object.id}")

        self.control_object.execute(device)
        return None
