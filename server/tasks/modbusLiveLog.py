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
                self.buffer[self.currentIx][i + 1] = self._readRegister(register)
            
            self.currentIx = (self.currentIx + 1) % self.size
        self.time = eventTime + 1.0 / self.frequency
        return self
    
    def _readRegister(self, register):
       if register['type'] == 'holding':
           return self.inverter.readFormatedHoldingRegister(register['address'], register['size'], register['endianess'])
