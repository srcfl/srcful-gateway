import logging
from server.app.blackboard import BlackBoard
from server.devices.Device import DeviceCommand, DeviceCommandStatus, DeviceCommandType, DeviceMode
from server.web.socket.control.control_messages.base_message import BaseMessage
from server.web.socket.control.control_messages.control_message import ControlMessage
from server.web.socket.control.control_messages.types import ControlMessageType, PayloadAction, PayloadActionType
from .task import Task
from server.web.socket.control.control_messages.modbus_message import ModbusMessage
from typing import List, Optional
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ControlDeviceTaskListener:

    def on_control_device_task_completed(self, task: 'ControlDeviceTask'):
        pass


class ControlDeviceTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, message: ControlMessage):
        super().__init__(event_time, bb)
        self.command: Optional[DeviceCommand] = None
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

        if self.is_cancelled:
            return None

        if self.command is None:
            # create the command
            der_sn = self.message.sn
            device = self.bb.devices.find_sn(der_sn)

            if device is None:
                logger.error(f"Device not found: {der_sn}")
                return None

            logger.info(f"Executing control object with id: {self.message.id}, message: {self.message.payload}")

            if self.message.type == ControlMessageType.EMS_PRE_SETUP:
                # TODO: we likely need some error checking here, possibly this can be done by adding a command to the device that will be executed
                # this could even be a dummy command that will just act as a callback thingamajig
                device.set_mode(DeviceMode.CONTROL)

                # for now we just count this as a success
                self.is_executed = True
                self.executed_at_timestamp = self.bb.time_ms()
                self.executed_successfully = True
                for listener in self.listeners:
                    listener.on_control_device_task_completed(self)
                return None
                
            elif self.message.type == ControlMessageType.EMS_CONTROL_SCHEDULE:
                logger.info(f"Message action: {self.message.action}")
                power = self.message.action.get(PayloadAction.POWER)
                action_type = self.message.action.get(PayloadAction.TYPE, PayloadActionType.NONE)

                if action_type == PayloadActionType.BATTERY_DISCHARGE:
                    self.command = DeviceCommand(DeviceCommandType.SET_BATTERY_POWER, -power)
                elif action_type == PayloadActionType.BATTERY_CHARGE:
                    self.command = DeviceCommand(DeviceCommandType.SET_BATTERY_POWER, power)
                else:
                    logger.error(f"Unknown action type: {self.message.action}")
                    logger.error(f"Unknown action type: {action_type}")
                    return None
            else:
                logger.error(f"Unknown control message type: {self.message.type}")
                return None
            

            if self.command is not None:
                device.add_command(self.command)
                self.time = self.bb.time_ms() + 2000 # recheck the command in 2 seconds

            return self

        else:

            if self.command.success == DeviceCommandStatus.SUCCESS:
                self.is_executed = True
                self.executed_at_timestamp = self.command.ts_executed
                self.executed_successfully = True
                for listener in self.listeners:
                    listener.on_control_device_task_completed(self)
                return None
            else: # TODO: this will count pending also as a failed command
                self.is_executed = True
                self.executed_at_timestamp = self.command.ts_executed
                self.executed_successfully = False
                for listener in self.listeners:
                    listener.on_control_device_task_completed(self)
                return None
            

            # TODO: recheck the command execution and notify listeners

            # self.message.process_commands(device)  # The message object is updated in place
            # self.is_executed = True
            # self.executed_at_timestamp = self.bb.time_ms()

            # Check if all commands were executed successfully
            # self.executed_successfully = all(command.success for command in self.message.commands)

            # for listener in self.listeners:
            #     listener.on_control_device_task_completed(self)

        return None

    def cancel(self):
        self.is_cancelled = True
