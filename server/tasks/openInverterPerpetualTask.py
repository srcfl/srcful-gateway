import logging

from server.blackboard import BlackBoard
from server.inverters.inverter import Inverter

from .task import Task

logger = logging.getLogger(__name__)


class OpenInverterPerpetualTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, inverter: Inverter):
        super().__init__(event_time, bb)
        self.inverter = inverter

    def execute(self, event_time):
        
        # has an inverter been opened?
        if len(self.bb.inverters.lst) > 0 and self.bb.inverters.lst[0].is_open():
            self.bb.inverters.remove(self.inverter)
            self.inverter.terminate()
            return

        try:
            logger.info("Inverter terminated: %s", self.inverter.is_terminated())

            if self.inverter.open(reconnect_delay=0, retries=3, timeout=5, reconnect_delay_max=0):
                # terminate and remove all inverters from the blackboard
                for i in self.bb.inverters.lst:
                    i.terminate()
                    self.bb.inverters.remove(i)

                self.bb.inverters.add(self.inverter)
                self.bb.add_info("Inverter opened: " + str(self.inverter.get_config()))

                return
            else:
                message = "Failed to open inverter, retry in 5 minutes: " + str(self.inverter.get_config())
                logger.info(message)
                self.bb.add_error(message)
                self.time = event_time + 60000 * 5
                return self
        except Exception as e:
            logger.exception("Exception opening inverter: %s", e)
            self.time = event_time + 10000
            return self