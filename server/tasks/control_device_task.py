import logging
from server.app.blackboard import BlackBoard
from .task import Task
from server.web.socket.control.control_messages.control_message import ControlMessage
from typing import List
import time
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ControlDeviceTaskListener:
    def on_control_device_task_started(self, task: 'ControlDeviceTask'):
        pass

    def on_control_device_task_completed(self, task: 'ControlDeviceTask'):
        pass


class ControlDeviceTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, control_message: ControlMessage):
        super().__init__(event_time, bb)
        self.control_message = control_message
        self.is_cancelled = False
        self.is_executed = False
        self.executed_at_timestamp = None
        self.is_acked = False
        self.is_nacked = False

        self.listeners: List[ControlDeviceTaskListener] = []

        logger.info(f"Control device task with id {self.control_message.id} initialized and will execute at {self.time}")

    def register_listener(self, listener: ControlDeviceTaskListener):
        self.listeners.append(listener)

    def unregister_listener(self, listener: ControlDeviceTaskListener):
        self.listeners.remove(listener)

    def execute(self, event_time):

        if not self.is_cancelled:
            der_sn = self.control_message.sn
            device = self.bb.devices.find_sn(der_sn)

            if device is None:
                logger.error(f"Device not found: {der_sn}")
                return None

            logger.info(f"Executing control object with id: {self.control_message.id}, message: {self.control_message}")

            self.control_message = self.control_message.process_commands(device)  # returns an updated control message
            self.is_executed = True  # we have executed the task
            self.executed_at_timestamp = self.bb.time_ms()

            for listener in self.listeners:
                listener.on_control_device_task_completed(self)

        return None
