import logging
from server.app.blackboard import BlackBoard
from server.devices.IComFactory import IComFactory
from .task import Task
from server.devices.ICom import ICom
from server.network.network_utils import NetworkUtils


logger = logging.getLogger(__name__)


class DevicePerpetualTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device: ICom):
        super().__init__(event_time, bb)
        self.device: ICom = device
        # self.old_device: Optional[ICom] = None

    def in_storage(self, device: ICom):
        connections = self.bb.device_storage.get_connections()
        for connection in connections:
            settings_device = IComFactory.create_com(connection)
            if settings_device.get_SN() == device.get_SN():
                return True
        return False

    def in_settings(self, device: ICom):
        for settings in self.bb.settings.devices.connections:
            settings_device = IComFactory.create_com(settings)
            if settings_device.get_SN() == device.get_SN():
                return True
        return False

    def execute(self, event_time):
        logger.info("*************************************************************")
        logger.info("******************** DevicePerpetualTask ********************")
        logger.info("*************************************************************")

        logger.info("DevicePerpetualTask got device: %s", self.device.get_config())

        """
        Check if the device is already in the blackboard and is open. 
        If it is, we don't need to do anything. This check is necessary to ensure
        that a device does not get opened multiple times.
        """
        existing_device = self.bb.devices.find_sn(self.device.get_SN())
        if existing_device and existing_device.is_open():
            logger.info("Device is already open, skipping")
            return None

        # If the device is not in the storage list it has probably been closed so lets not do anything
        if not self.in_storage(self.device) and not self.in_settings(self.device):  # To-Do: remove the second part (not self.in_settings(self.device)) of the and once we release 0.22.7
            logger.info("Device is not in settings, skipping")
            return None

        try:
            if self.device.connect():
                logger.info("Device connected: %s", self.device.get_config())

                if self.bb.devices.contains(self.device) and not self.device.is_open():
                    message = "Device is already in the blackboard, no action needed"
                    logger.info(message)
                    self.bb.add_warning(message)
                    return None

                message = "Device opened: " + str(self.device.get_config())
                logger.info(message)

                self.bb.devices.add(self.device)
                return None

            else:

                tmp_device = self.device.find_device()  # find the device on the network this is the same device but the method of connection (e.g. ip can be different)

                if tmp_device is not None:

                    self.device = tmp_device
                    logger.info("Found a device at %s, retrying in 5 seconds...", self.device.get_config())
                    self.time = event_time + 5000
                    self.bb.add_info("Found a device at " + self.device.get_name() + ", retrying in 5 seconds...")
                else:
                    message = f"Failed to find {self.device.get_name()} ({self.device.get_SN()}), rescanning again in 5 minutes..."
                    logger.info(message)
                    self.bb.add_error(message)
                    self.time = event_time + 60000 * 5

            return self

        except Exception as e:
            logger.exception("Exception opening a device: %s", e)
            self.time = event_time + 10000
            return self
