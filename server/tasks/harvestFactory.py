from server.blackboard import BlackBoard
from .harvest import Harvest
from .harvestTransport import DefaultHarvestTransportFactory
from server.settings import ChangeSource


class HarvestFactory:
    """This class is responsible for creating harvest tasks when inverters are added to the blackboard."""

    def __init__(self, bb: BlackBoard):
        self.bb = bb
        bb.devices.add_listener(self)

    def add_device(self, com):
        # now we have an open device, lets create a harvest task and save it to the settings
        if com.is_open():
            self.bb.add_task(Harvest(self.bb.time_ms() + 1000, self.bb, com,  DefaultHarvestTransportFactory()))
            self.bb.settings.devices.add_connection(com, ChangeSource.LOCAL)    
    
    def remove_device(self, inverter):
        pass
