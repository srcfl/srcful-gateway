from .task import Task
from server.blackboard import BlackBoard


class ModbusLiveLogTask(Task):
    def __init__(self, inverter, frequency, registers, size, bb: BlackBoard):
        super().__init__(1000 // frequency, bb)
        self.inverter = inverter
        self.frequency = frequency
        self.registers = registers
        self.size = size
        self.currentIx = 0
        self.buffer = [[None] * len(registers)] * size

    def execute(self, event_time):
        if self.inverter.isTerminated():
            return None

        try:
            self.buffer[self.currentIx][0] = event_time
            for i, register in enumerate(self.registers):
                self.buffer[self.currentIx][i + 1] = register.readValue(self.inverter)[
                    1
                ]

            self.currentIx = (self.currentIx + 1) % self.size
        except Exception as e:
            self.buffer[self.currentIx][1] = "Error: " + str(e)

        self.time = event_time + 1.0 / self.frequency
        return self
