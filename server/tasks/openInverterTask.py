import logging

from server.blackboard import BlackBoard
from server.inverters.inverter import Inverter

from .task import Task

logger = logging.getLogger(__name__)


class ReadFreq(Task):
    def __init__(self, event_time: int, bb: BlackBoard, inverter: Inverter):
        super().__init__(event_time, bb)
        self.inverter = inverter
        # self.stats['lastFreq'] = 'n/a'

    def execute(self, event_time) -> Task or list[Task]:
        try:
            freq = self.inverter.readFrequency()
            logger.info("freq: %s", freq)
            # self.stats['lastFreq'] = freq
            # self.stats['freqReads'] += 1
        except Exception:
            logger.error("error reading freq")
            return None

        self.time = event_time + 100
        return self


class OpenInverterTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, inverter: Inverter):
        super().__init__(event_time, bb)
        self.inverter = inverter

    def execute(self, event_time):
        # Do this n times?
        try:
            if self.inverter.open(reconnect_delay=0, retries=3, timeout=5, reconnect_delay_max=0):
                # terminate and remove all inverters from the blackboard
                for i in self.bb.inverters.lst:
                    i.terminate()
                    self.bb.inverters.remove(i)

                self.bb.inverters.add(self.inverter)
                self.bb.add_info("Inverter opened: " + str(self.inverter.get_config()))

                # if 'inverter' in self.stats and self.stats['inverter'] != None:
                #  self.stats['inverter'].terminate()
                # self.stats['inverter'] = self.inverter
                # if(self.bootstrap != None):
                #  self.bootstrap.appendInverter(self.inverter.getConfig())
                return
            else:
                self.inverter.terminate()
                message = "Failed to open inverter: " + str(self.inverter.get_config())
                logger.info(message)
                self.bb.add_error(message)
                return None
        except Exception as e:
            logger.exception("Exception opening inverter: %s", e)
            self.time = event_time + 10000
            return self
