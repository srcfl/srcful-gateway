import logging
from server.devices.modbus import Modbus
from server.blackboard import BlackBoard
from .task import Task

log = logging.getLogger(__name__)


class ModbusWriteTask(Task):
    class Command:
        def __init__(self, command_type):
            self.type = command_type

    class WriteCommand(Command):
        def __init__(self, staring_address, values):
            super().__init__("write")
            self.starting_address = staring_address
            self.values = values

    class PauseCommand(Command):
        def __init__(self, duration):
            super().__init__("pause")
            self.duration = duration

    def __init__(self, event_time: int, bb: BlackBoard, inverter: Modbus, commands: list[Command]):
        super().__init__(event_time, bb)
        self.inverter = inverter
        self.current_command = 0
        self.commands = commands

    def execute(self, event_time) -> None | Task | list[Task]:
        if self.current_command >= len(self.commands):
            return None

        while self.current_command < len(self.commands):
            command = self.commands[self.current_command]
            if isinstance(command, ModbusWriteTask.WriteCommand):
                try:
                    self.inverter.write_registers(
                        command.starting_address, command.values
                    )
                except Exception as e:
                    log.error("Failed to write to Modbus device: %s", e)
                self.current_command += 1
            elif isinstance(command, ModbusWriteTask.PauseCommand):
                self.time = event_time + command.duration
                self.current_command += 1
                return self
            else:
                log.error("Unknown command type: %s", command.type)
                return None

        return None
