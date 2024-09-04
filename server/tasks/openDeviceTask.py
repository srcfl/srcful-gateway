import logging

from server.blackboard import BlackBoard
from server.inverters.modbus import Modbus
from .task import Task
from ..inverters.ICom import ICom

logger = logging.getLogger(__name__)


class OpenDeviceTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device: ICom):
        super().__init__(event_time, bb)
        self.device = device

    def execute(self, event_time):
        logger.info("##########################################################")
        logger.info("#################### OpenDeviceTask ####################")
        logger.info("##########################################################")
        try:
            if self.device.connect():
                logger.info("Opening: %s", self.device.get_config())
                
                # terminate and remove all inverters from the blackboard
                for i in self.bb.devices.lst:
                    i.disconnect()
                    self.bb.devices.remove(i)
                
                logger.info("Device opened: %s", self.device.get_config())

                self.bb.devices.add(self.device)
                self.bb.add_info("Device opened: " + str(self.device.get_config()))

                return None
            else:
                self.device.disconnect()
                message = "Failed to open device: " + str(self.device.get_config())
                logger.info(message)
                self.bb.add_error(message)
                return None
        except Exception as e:
            logger.exception("Exception opening device: %s", e)
            self.time = event_time + 10000
            return self
