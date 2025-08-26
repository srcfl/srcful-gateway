import logging
from server.app.blackboard import BlackBoard
from .task import Task
from server.control.control_messages.modbus_message import ModbusMessage
from typing import List
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ControlDeviceTaskListener:

    def on_control_device_task_completed(self, task: 'ControlDeviceTask'):
        pass


class ControlDeviceTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, message: ModbusMessage):
        super().__init__(event_time, bb)
        self.message = message
        self.is_cancelled = False
        self.is_executed = False
        self.executed_successfully = False
        self.executed_at_timestamp = None
        self.is_acked = False
        self.is_nacked = False

        self.listeners: List[ControlDeviceTaskListener] = []

        logger.info(f"Control device task with id {self.message.id} initialized and will execute at {self.time}")

    def register_listener(self, listener: ControlDeviceTaskListener):
        self.listeners.append(listener)

    def unregister_listener(self, listener: ControlDeviceTaskListener):
        self.listeners.remove(listener)

    def execute(self, event_time):

        if not self.is_cancelled:
            der_sn = self.message.sn
            device = self.bb.devices.find_sn(der_sn)

            if device is None:
                logger.error(f"Device not found: {der_sn}")
                return None

            logger.info(f"Executing control object with id: {self.message.id}, message: {self.message.payload}")

            self.message.process_commands(device)  # The message object is updated in place
            self.is_executed = True
            self.executed_at_timestamp = self.bb.time_ms()

            # Check if all commands were executed successfully
            self.executed_successfully = all(command.success for command in self.message.commands)

            for listener in self.listeners:
                listener.on_control_device_task_completed(self)

        return None

    def cancel(self):
        self.is_cancelled = True
