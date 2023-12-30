import server.inverters.registerValue as RegisterValue
import server.inverters.inverter as Inverter

class ModbusLiveLogTask(Task):

    def __init__(self, inverter, frequency, registers, size):
        super().__init__()
        self.inverter = inverter
        self.frequency = frequency
        self.registers = registers
        self.size = size
        self.currentIx = 0
        self.buffer = [[None] * len(registers)] * size

    def execute(self, eventTime):

        if self.inverter.isTerminated():
            return None
        
        try:
            self.buffer[self.currentIx][0] = eventTime
            for i, register in enumerate(self.registers):

                self.buffer[self.currentIx][i + 1] = register.readValue(self.inverter)[1]
            
            self.currentIx = (self.currentIx + 1) % self.size
        except Exception as e:
            self.buffer[self.currentIx][1] = 'Error: ' + str(e)

        self.time = eventTime + 1.0 / self.frequency
        return self