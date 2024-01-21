from .task import Task
from server.inverters.inverter import Inverter
from server.blackboard import BlackBoard
import logging

log = logging.getLogger(__name__)


class ModbusWriteTask(Task):
    class Command:
        def __init__(self, type):
            self.type = type

    class WriteCommand(Command):
        def __init__(self, staring_address, values):
            super().__init__("write")
            self.startingAddress = staring_address
            self.values = values

    class PauseCommand(Command):
        def __init__(self, duration):
            super().__init__("pause")
            self.duration = duration

    def __init__(
        self,
        event_time: int,
        bb: BlackBoard,
        inverter: Inverter,
        commands: list[Command],
    ):
        super().__init__(event_time, bb)
        self.inverter = inverter
        self.currentCommand = 0
        self.commands = commands

    def execute(self, event_time) -> None | Task | list[Task]:
        if self.currentCommand >= len(self.commands):
            return None

        while self.currentCommand < len(self.commands):
            command = self.commands[self.currentCommand]
            if isinstance(command, ModbusWriteTask.WriteCommand):
                try:
                    self.inverter.write_registers(
                        command.startingAddress, command.values
                    )
                except Exception as e:
                    log.error("Failed to write to Modbus device: %s", e)
                self.currentCommand += 1
            elif isinstance(command, ModbusWriteTask.PauseCommand):
                self.time = event_time + command.duration
                self.currentCommand += 1
                return self
            else:
                log.error("Unknown command type: %s", command.type)
                return None

        return None
