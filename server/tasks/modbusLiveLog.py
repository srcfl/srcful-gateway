from server.blackboard import BlackBoard
from .task import Task


class ModbusLiveLogTask(Task):
    def __init__(self, inverter, frequency, registers, size, bb: BlackBoard):
        super().__init__(1000 // frequency, bb)
        self.inverter = inverter
        self.frequency = frequency
        self.registers = registers
        self.size = size
        self._current_ix = 0
        self.buffer = [[None] * len(registers)] * size

    def execute(self, event_time):
        if self.inverter.isTerminated():
            return None

        try:
            self.buffer[self._current_ix][0] = event_time
            for i, register in enumerate(self.registers):
                self.buffer[self._current_ix][i + 1] = register.readValue(self.inverter)[
                    1
                ]

            self._current_ix = (self._current_ix + 1) % self.size
        except Exception as e:
            self.buffer[self._current_ix][1] = "Error: " + str(e)

        self.time = event_time + 1.0 / self.frequency
        return self
