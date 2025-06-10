
import logging
from typing import List, Union
from server.devices.Device import DeviceMode
from server.tasks.itask import ITask
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.app.blackboard import BlackBoard

from .harvestableTask import HarvestableTask
from .harvestTransport import ITransportFactory
from server.devices.ICom import ICom

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class Harvest(HarvestableTask):
    def __init__(self, event_time: int, bb: BlackBoard, device: ICom, transport_factory: ITransportFactory):
        super().__init__(event_time, bb, device, transport_factory)
        self.backoff_time = 1000  # start with a 1000ms backoff

    def execute(self, event_time) -> Union[List[ITask], ITask, None]:

        start_time = event_time
        elapsed_time_ms = 1000

        if not self.device.is_open():
            logger.info("Device is closed make the final transport if there is anything in the barn")
            # self.bb.devices.remove(self.device)
            # self.bb.add_warning("Device unexpectedly closed, removing from blackboard and starting a new open device perpetual task")

            transports = self._create_transport(event_time, self.bb.settings.harvest.endpoints, force_transport=True)

            #  if the devices is not terminated, we need to start a new open device perpetual to try to reconnect
            if not self.device.is_disconnected():

                logger.info("Disconnecting device from harvest task")
                self.device.disconnect()

                open_inverter = DevicePerpetualTask(event_time + 30000, self.bb, self.device.clone())
                transports.append(open_inverter)

            return transports

        try:

            if hasattr(self.device, 'get_mode') and self.device.get_mode() == DeviceMode.CONTROL:
                logger.info("Device is in control mode, going to power limit controller task")
                from server.tasks.powerLimitControllerTask import PowerLimitControllerTask
                return PowerLimitControllerTask(self.bb.time_ms() + 1000, self.bb, self.device)

            harvest = self.collect_harvest_data(start_time)
            elapsed_time_ms = self.bb.time_ms() - start_time
            self.backoff_time = self.device.get_backoff_time_ms(elapsed_time_ms, self.backoff_time)
            logger.debug("Harvest from [%s] took %s ms. Data points: %s", self.device.get_SN(), elapsed_time_ms, len(harvest))

        except Exception as e:

            # To-Do: Solarmanv5 can raise ConnectionResetError, so handle it!

            self.device.disconnect()

            clone = self.device.clone()
            open_inverter = DevicePerpetualTask(self.bb.time_ms() + 30000, self.bb, clone)
            transports = self._create_transport(self.bb.time_ms(), self.bb.settings.harvest.endpoints, force_transport=True)

            return [open_inverter] + transports

        # If we're reading faster than every 1000ms, we subtract the elapsed time of
        # the current harvest from the backoff time to keep polling at a constant rate of every 1000ms
        if elapsed_time_ms < self.backoff_time:
            self.time = self.bb.time_ms() + self.backoff_time - elapsed_time_ms
        else:
            self.time = self.bb.time_ms() + self.backoff_time

        # check if it is time to transport the harvest
        transport = self._create_transport(self.bb.time_ms() + elapsed_time_ms * 2, self.bb.settings.harvest.endpoints)
        if len(transport) > 0:
            return [self] + transport
        return self
