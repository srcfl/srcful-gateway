
import logging
import requests

from server.inverters.inverter import Inverter
from server.blackboard import BlackBoard
import server.crypto.crypto as atecc608b

from .task import Task
from .srcfulAPICallTask import SrcfulAPICallTask

log = logging.getLogger(__name__)


class Harvest(Task):
    def __init__(self, event_time: int, bb: BlackBoard, inverter: Inverter):
        super().__init__(event_time, bb)
        self.inverter = inverter
        # self.stats['lastHarvest'] = 'n/a'
        # self.stats['harvests'] = 0
        self.barn = {}
        self.transport = None

        # incremental backoff stuff
        self.backoff_time = 1000  # start with a 1-second backoff
        self.max_backoff_time = 256000  # max ~4.3-minute backoff

    def execute(self, event_time) -> Task | list[Task]:
        if self.inverter.is_terminated():
            return None

        try:
            harvest = self.inverter.read_harvest_data()
            # self.stats['lastHarvest'] = harvest
            # self.stats['harvests'] += 1
            self.barn[event_time] = harvest

            self.backoff_time = max(self.backoff_time - self.backoff_time * 0.1, 1000)

        except Exception as e:
            self._handle_harvest_exception(e)

        self.time = event_time + self.backoff_time

        # check if it is time to transport the harvest
        if (self._is_time_to_transport()):

            self.transport = HarvestTransport(
                event_time + 100, self.bb, self.barn, self.inverter.get_type()
            )
            self.barn.clear()
            return [self, self.transport]

        return self

    def _is_time_to_transport(self):
        return (len(self.barn) >= 10 and len(self.barn) % 10 == 0) and (
              self.transport is None or self.transport.reply is not None)

    def _reopen_inverter(self):
        log.info(
            "Max backoff time reached, trying to close and reopen inverter at: %s:%s",
            self.inverter.get_address(),
            self.inverter.get_port(),
        )
        if self.inverter.is_open():
            self.inverter.close()
        else:
            if not self.inverter.open():
                log.error("FAILED to reopen inverter: %s", self.inverter.get_config_dict())

    def _handle_harvest_exception(self, e: Exception):
        if self.backoff_time == self.max_backoff_time:
            self._reopen_inverter()
        else:
            log.debug("Handling exeption reading harvest: %s", str(e))
            self.backoff_time = min(self.backoff_time * 2, self.max_backoff_time)
            log.info("Incrementing backoff time to: %s", self.backoff_time)


class HarvestTransport(SrcfulAPICallTask):
    def __init__(self, event_time: int, bb: BlackBoard, barn: dict, inverter_type: str):
        super().__init__(event_time, bb)
        # self.stats['lastHarvestTransport'] = 'n/a'
        # if 'harvestTransports' not in self.stats:
        #  self.stats['harvestTransports'] = 0
        self.barn_ref = barn
        self.barn = dict(barn)
        self.inverter_type = inverter_type

    def _data(self):
        atecc608b.init_chip()
        jwt = atecc608b.build_jwt(self.barn, self.inverter_type)
        atecc608b.release()
        return jwt

    def _on_200(self, reply):
        print("Response:", reply)
        # self.stats['harvestTransports'] += 1

    def _on_error(self, reply: requests.Response):
        log.warning("Error in harvest transport: %s", str(reply))
        return 0
