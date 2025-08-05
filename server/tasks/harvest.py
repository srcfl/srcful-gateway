
import logging
from typing import List, Union
from server.tasks.itask import ITask
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.app.blackboard import BlackBoard
from .task import Task
from .harvestTransport import ITransportFactory
from server.devices.ICom import ICom
from server.diagnostics.solarman_logger import get_diagnostic_logger
from server.devices.inverters.ModbusSolarman import ModbusSolarman

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class Harvest:
    def __init__(self):
        self.backoff_time = 1000  # start with a 1000ms backoff
        self.harvest_count = 0
        self.total_harvest_time_ms = 0
        self.last_stats_time = 0  # Track when we last logged statistics
        self.stats_interval_ms = 5 * 60 * 1000  # 5 minutes in milliseconds
        self.diagnostic_logger = get_diagnostic_logger()

    def harvest(self, event_time: int, device: ICom, bb: BlackBoard) -> tuple[int, dict]:

        start_time = event_time
        elapsed_time_ms = 1000

        # Check if we should log statistics (every 5 minutes)
        if self.last_stats_time == 0:
            self.last_stats_time = event_time

        if event_time - self.last_stats_time >= self.stats_interval_ms:
            self._log_periodic_statistics(device, event_time)
            self.last_stats_time = event_time

        try:
            harvest = device.read_harvest_data(force_verbose=self.harvest_count % 10 == 0)
            self.harvest_count += 1
            end_time = bb.time_ms()

            elapsed_time_ms = end_time - start_time
            self.backoff_time = device.get_backoff_time_ms(elapsed_time_ms, self.backoff_time)
            logger.debug("Harvest from [%s] took %s ms. Data points: %s", device.get_SN(), elapsed_time_ms, len(harvest))

            self.total_harvest_time_ms += elapsed_time_ms

        except Exception as e:
            # Log exception with ping test for solarman devices
            if isinstance(device, ModbusSolarman):
                self.diagnostic_logger.log_exception(
                    device, e, self.harvest_count, self.total_harvest_time_ms, self.backoff_time
                )
                logger.error("Solarman device exception logged with diagnostics: %s", str(e))

            # To-Do: Solarmanv5 can raise ConnectionResetError, so handle it!
            raise ICom.ConnectionException("Error harvesting from device", device, e)

        # If we're reading faster than every 1000ms, we subtract the elapsed time of
        # the current harvest from the backoff time to keep polling at a constant rate of every 1000ms
        if elapsed_time_ms < self.backoff_time:
            next_time = bb.time_ms() + self.backoff_time - elapsed_time_ms
        else:
            next_time = bb.time_ms() + self.backoff_time

        return next_time, harvest

    def _log_periodic_statistics(self, device: ICom, event_time: int):
        """Log periodic statistics for solarman devices"""
        if isinstance(device, ModbusSolarman):
            # Calculate average harvest time
            avg_harvest_time = (self.total_harvest_time_ms / self.harvest_count) if self.harvest_count > 0 else 0

            additional_stats = {
                "avg_harvest_time_ms": avg_harvest_time,
                "event_time": event_time,
                "stats_interval_ms": self.stats_interval_ms
            }

            self.diagnostic_logger.log_statistics(
                device,
                self.harvest_count,
                self.total_harvest_time_ms,
                self.backoff_time,
                additional_stats
            )

            logger.info(
                f"Logged 5-minute statistics for {device.get_SN()}: "
                f"{self.harvest_count} harvests, avg time: {avg_harvest_time:.1f}ms"
            )
