
import logging
from typing import List, Union
from server.tasks.itask import ITask
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.app.blackboard import BlackBoard
from .task import Task
from .harvestTransport import ITransportFactory
from server.devices.ICom import ICom

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class Harvest:
    def __init__(self):
        self.backoff_time = 1000  # start with a 1000ms backoff
        self.harvest_count = 0
        self.total_harvest_time_ms = 0

    def harvest(self, event_time:int, device: ICom, bb: BlackBoard) -> tuple[int, dict]:

        start_time = event_time
        elapsed_time_ms = 1000

        try:
            harvest = device.read_harvest_data(force_verbose=self.harvest_count % 10 == 0)
            self.harvest_count += 1
            end_time = bb.time_ms()

            elapsed_time_ms = end_time - start_time
            self.backoff_time = device.get_backoff_time_ms(elapsed_time_ms, self.backoff_time)
            logger.debug("Harvest from [%s] took %s ms. Data points: %s", device.get_SN(), elapsed_time_ms, len(harvest))

            self.total_harvest_time_ms += elapsed_time_ms

        except Exception as e:
            # To-Do: Solarmanv5 can raise ConnectionResetError, so handle it!
            raise ICom.ConnectionException("Error harvesting from device", device, e)

        # If we're reading faster than every 1000ms, we subtract the elapsed time of
        # the current harvest from the backoff time to keep polling at a constant rate of every 1000ms
        if elapsed_time_ms < self.backoff_time:
            next_time = bb.time_ms() + self.backoff_time - elapsed_time_ms
        else:
            next_time = bb.time_ms() + self.backoff_time

        return next_time, harvest    