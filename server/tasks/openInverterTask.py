import logging

from server.blackboard import BlackBoard
from server.inverters.modbus import Modbus
from .task import Task
from ..inverters.der import DER

logger = logging.getLogger(__name__)


class OpenInverterTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, der: DER):
        super().__init__(event_time, bb)
        self.der = der

    def execute(self, event_time):
        logger.info("##########################################################")
        logger.info("#################### OpenInverterTask ####################")
        logger.info("##########################################################")
        try:
            if self.der.connect():
                logger.info("Opening: %s", self.der.get_config())
                
                # terminate and remove all inverters from the blackboard
                for i in self.bb.ders.lst:
                    i.disconnect()
                    self.bb.ders.remove(i)
                
                logger.info("DER opened: %s", self.der.get_config())

                self.bb.ders.add(self.der)
                self.bb.add_info("Inverter opened: " + str(self.der.get_config()))

                return None
            else:
                self.der.disconnect()
                message = "Failed to open DER: " + str(self.der.get_config())
                logger.info(message)
                self.bb.add_error(message)
                return None
        except Exception as e:
            logger.exception("Exception opening DER: %s", e)
            self.time = event_time + 10000
            return self
