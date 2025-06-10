import logging
from server.app.blackboard import BlackBoard
from .task import Task
from server.devices.inverters.ModbusTCP import ModbusTCP

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PowerLimitControllerTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, der_sn: str):
        super().__init__(event_time, bb)
        self.device: ModbusTCP = self.bb.devices.find_sn(der_sn)

    def execute(self, event_time):

        if self.device is None:
            logger.error(f"Device not found: {self.der_sn}")
            return None

        # if not inited check here

        if self.device.profile.init_device(self.device):
            logging.info(f"Successfully initialized device {self.der_sn}")
        else:
            logging.error(f"Failed to initialize device {self.der_sn}")

        # deinit check here
        if self.device.profile.deinit_device(self.device):
            logging.info(f"Successfully deinitialized device {self.der_sn}")
        else:
            logging.error(f"Failed to deinitialize device {self.der_sn}")
        pass

        # logic function
