import server.crypto.crypto as crypto
import time

class BlackBoard:
    '''
    Blackboard class is the subject class of the observer pattern.
    It is responsible for maintaining the state of the system and notifying
    the observers when the state changes.
    '''

    def __init__(self):
        self._inverters = BlackBoard.Inverters()
        self._startTime = self.time_ms()

    @property
    def inverters(self):
        return self._inverters

    @property
    def startTime(self):
        return self._startTime

    def getChipInfo():
        crypto.initChip()

        device_name = crypto.getDeviceName()
        serial_number = crypto.getSerialNumber().hex()

        crypto.release()

        return 'device: ' + device_name + ' serial: ' + serial_number


    def time_ms():
        return time.time_ns() // 1_000_000
    
    class Inverters:
        '''Observable list of inverters'''
        def __init__(self):
            self.lst = []
            self._observers = []
        
        def add(self, inverter):
            self._inverters.append(inverter)
            for o in self._observers:
                o.addInverter(inverter)
        
        def removeInverter(self, inverter):
            self._inverters.remove(inverter)
            for o in self._observers:
                o.remove(inverter)
        