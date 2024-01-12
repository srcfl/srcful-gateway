import server.crypto.crypto as crypto
import time

class BlackBoard:
    '''
    Blackboard class is the subject class of the observer pattern.
    It is responsible for maintaining the state of the system and notifying
    the observers when the state changes.
    '''

    def __init__(self):
        self.inverters = BlackBoard.Inverters()


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
            self.inverters = []
            self._observers = []
        
        def add(self, inverter):
            self._inverters.append(inverter)
            for o in self._observers:
                o.add(inverter)
        
        def remove(self, inverter):
            self._inverters.remove(inverter)
            for o in self._observers:
                o.remove(inverter)
        