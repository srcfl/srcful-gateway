from server.blackboard import BlackBoard
from .harvest import Harvest, DefaultHarvestTransportFactory


class HarvestFactory:
    """This class is responsible for creating harvest tasks when inverters are added to the blackboard."""

    def __init__(self, bb: BlackBoard):
        self.bb = bb
        bb.inverters.add_listener(self)

    def add_inverter(self, inverter):
        return self.bb.add_task(Harvest(self.bb.time_ms() + 1000, self.bb, inverter,  DefaultHarvestTransportFactory()))
    
    def remove_inverter(self, inverter):
        pass

    def dummy(self):
        pass