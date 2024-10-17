from server.blackboard import BlackBoard
from .harvest import Harvest
from .harvestTransport import DefaultHarvestTransportFactory
from server.settings import ChangeSource
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class HarvestFactory:
    """This class is responsible for creating harvest tasks when inverters are added to the blackboard."""

    def __init__(self, bb: BlackBoard):
        self.bb = bb
        bb.devices.add_listener(self)

    def add_device(self, com):
        """Add the device to the blackboard and create a harvest task and save it to the settings"""
        # now we have an open device, lets create a harvest task and save it to the settings
        if com.is_open():
            self.bb.add_task(Harvest(self.bb.time_ms() + 1000, self.bb, com,  DefaultHarvestTransportFactory()))
            self.bb.settings.devices.add_connection(com, ChangeSource.LOCAL)
    
    def remove_device(self, com):
        """Remove the device from the blackboard and disconnect it"""
        try:
            com.disconnect()
        except ValueError:
            logger.warning("Device %s already disconnected", com)
        self.bb.settings.devices.remove_connection(com, ChangeSource.LOCAL)
