from server.blackboard import BlackBoard
from .harvest import Harvest
from .harvestTransport import DefaultHarvestTransportFactory


class HarvestFactory:
    """This class is responsible for creating harvest tasks when inverters are added to the blackboard."""

    def __init__(self, bb: BlackBoard):
        self.bb = bb
        bb.devices.add_listener(self)

    def add_device(self, inverter):
        return self.bb.add_task(Harvest(self.bb.time_ms() + 1000, self.bb, inverter,  DefaultHarvestTransportFactory()))
    
    def remove_device(self, inverter):
        pass
