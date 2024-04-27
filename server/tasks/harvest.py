
import logging

from server.inverters.inverter import Inverter
from server.tasks.openInverterPerpetualTask import OpenInverterPerpetualTask
from server.blackboard import BlackBoard

from .task import Task
from .harvestTransport import ITransportFactory

log = logging.getLogger(__name__)


class Harvest(Task):
    def __init__(self, event_time: int, bb: BlackBoard, inverter: Inverter, transport_factory: ITransportFactory):
        super().__init__(event_time, bb)
        self.inverter = inverter
        # self.stats['lastHarvest'] = 'n/a'
        # self.stats['harvests'] = 0
        self.barn = {}
        self.min_backoff_time = 1000
        # incremental backoff stuff
        self.backoff_time = self.min_backoff_time  # start with a 1-second backoff
        self.max_backoff_time = 256000  # max ~4.3-minute backoff
        self.transport_factory = transport_factory

    def execute(self, event_time) -> Task | list[Task]:

        start_time = event_time
        elapsed_time_ms = 1000

        if self.inverter.is_terminated():
            log.info("Inverter is terminated make the final transport if there is anything in the barn")
            return self._create_transport(1, event_time=event_time)
        try:
            harvest = self.inverter.read_harvest_data(force_verbose=len(self.barn) == 0)
            end_time = self.bb.time_ms()

            elapsed_time_ms = end_time - start_time
            log.debug("Harvest took %s ms", elapsed_time_ms)
            # log.debug("Harvest: %s", harvest)

            self.min_backoff_time = max(elapsed_time_ms * 2, 1000)

            # self.stats['lastHarvest'] = harvest
            # self.stats['harvests'] += 1
            self.barn[event_time] = harvest

            self.backoff_time = max(self.backoff_time - self.backoff_time * 0.1, self.min_backoff_time)
            self.backoff_time = min(self.backoff_time, self.max_backoff_time)

        except Exception as e:
            log.debug("Handling exeption reading harvest: %s", str(e))
            
            end_time = self.bb.time_ms()

            elapsed_time_ms = end_time - start_time

            if self.backoff_time >= self.max_backoff_time:
                log.debug("Max timeout reached terminating inverter and issuing new reopen in 30 sec")
                self.inverter.terminate()
                open_inverter = OpenInverterPerpetualTask(event_time + 30000, self.bb, self.inverter.clone())
                self.time = event_time + 10000
                # we return self so that in the next execute the last harvest will be transported
                return [self, open_inverter]
            else:
                log.info("Incrementing backoff time to: %s", self.backoff_time)
                self.backoff_time = min(self.backoff_time * 2, self.max_backoff_time)
            
        self.time = event_time + self.backoff_time

        # check if it is time to transport the harvest
        transport = self._create_transport(10, event_time=event_time + elapsed_time_ms * 2)
        if (transport):
            return [self, transport]
        return self

    def _create_transport(self, limit: int, event_time: int):
        if (len(self.barn) > 0 and len(self.barn) % limit == 0):
            transport = self.transport_factory(event_time + 100, self.bb, self.barn, self.inverter)
            self.barn = {}
            return transport
        return None