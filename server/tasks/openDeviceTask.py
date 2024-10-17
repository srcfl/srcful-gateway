import logging

from server.blackboard import BlackBoard
from .task import Task
from ..inverters.ICom import ICom
from ..network.network_utils import NetworkUtils

logger = logging.getLogger(__name__)


class OpenDeviceTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device: ICom):
        super().__init__(event_time, bb)
        self.device = device

    def execute(self, event_time):
        logger.info("##########################################################")
        logger.info("#################### OpenDeviceTask ####################")
        logger.info("##########################################################")
        
        if self.bb.devices.contains(self.device): 
            logger.debug("Device is already in the blackboard, no action needed")
            return None
        
        try:
            if self.device.connect():
                if not self.device.is_valid():
                    self.device.disconnect()
                    message = "Failed to open device: " + str(self.device.get_config())
                    logger.error(message)
                    self.bb.add_error(message)
                    return None
                    
                message = "Device opened: " + str(self.device.get_config())
                logger.info(message)
                self.bb.devices.add(self.device)
                self.bb.add_info(message)

                return None
            else:
                self.device.disconnect()
                message = "Failed to open device: " + str(self.device.get_config())
                logger.error(message)
                self.bb.add_error(message)
                return None
            
        except Exception as e:
            logger.exception("Exception opening device: %s", e)
            message = "Failed to open device: " + str(self.device.get_config())
            self.bb.add_error(message)
            self.time = event_time + 10000
            return None
        
    def _is_open(self, device: ICom):
        for i in self.bb.devices.lst:
            if i.get_config() == device.get_config() and i.is_open():
                return True
        return False
