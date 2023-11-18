from .task import Task
from server.inverters.inverter import Inverter
import logging
log = logging.getLogger(__name__)


class ModbusWriteTask(Task):


    class Command:
        def __init__(self, type):
            self.type = type

    class WriteCommand(Command):
        def __init__(self, startingAddress, values):
            super().__init__('write')
            self.startingAddress = startingAddress
            self.values = values

    class PauseCommand(Command):
        def __init__(self, duration):
            super().__init__('pause')
            self.duration = duration


    def __init__(self, eventTime: int, stats: dict, inverter: Inverter, commands: list[Command]):
        super().__init__(eventTime, stats)
        self.inverter = inverter
        self.currentCommand = 0
        self.commands = commands

    def execute(self, eventTime) -> None | Task | list[Task]:
        if self.currentCommand >= len(self.commands):
            return None
        
        while self.currentCommand < len(self.commands):
            command = self.commands[self.currentCommand]
            if isinstance(command, ModbusWriteTask.WriteCommand):
                self.inverter.writeRegisters(command.startingAddress, command.values)
                self.currentCommand += 1
            elif isinstance(command, ModbusWriteTask.PauseCommand):
                self.time = eventTime + command.duration
                self.currentCommand += 1
                return self
            else:
                log.error('Unknown command type: %s', command.type)
                return None
        
        return None
        