import logging
from server.app.blackboard import BlackBoard
from server.devices.Device import Device, DeviceMode
from server.tasks.harvest import Harvest
from server.tasks.harvestTransport import DefaultHarvestTransportFactory
from .task import Task

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PowerLimitControllerTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device:Device):
        super().__init__(event_time, bb)
        self.device: Device = device
        self.is_initialized = False

    def execute(self, event_time):

        if self.device is None:
            logger.error(f"Device not found: {self.device.get_SN()}")
            return None

        # if not inited check here
        if not self.is_initialized:
            if self.device.profile.init_device(self.device):
                logging.info(f"Successfully initialized device {self.device.get_SN()}")
                self.is_initialized = True
            else:
                logging.error(f"Failed to initialize device {self.device.get_SN()}")

        # deinit check here
        if self.device.get_mode() == DeviceMode.READ:
            #if self.is_initialized:
            if self.device.profile.deinit_device(self.device):
                logging.info(f"Successfully deinitialized device {self.device.get_SN()}")
                self.is_initialized = False
            else:
                logging.error(f"Failed to deinitialize device {self.device.get_SN()}")

            logging.info(f"Device {self.device.get_SN()} is in read mode, go to harvest")

            return Harvest(event_time, self.bb, self.device, DefaultHarvestTransportFactory())

        self.time = self.bb.time_ms() + 1000

        return self

        # logic function
