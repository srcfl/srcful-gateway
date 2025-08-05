import logging
from server.app.blackboard import BlackBoard
from server.devices.IComFactory import IComFactory
from .task import Task
from server.devices.ICom import ICom
from server.network.network_utils import NetworkUtils
from server.diagnostics.solarman_logger import get_diagnostic_logger
from server.devices.inverters.ModbusSolarman import ModbusSolarman


logger = logging.getLogger(__name__)


class DevicePerpetualTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device: ICom):
        super().__init__(event_time, bb)
        self.device: ICom = device
        # self.old_device: Optional[ICom] = None
        self.diagnostic_logger = get_diagnostic_logger()

    def in_settings(self, device: ICom):
        for settings in self.bb.settings.devices.connections:
            settings_device = IComFactory.create_com(settings)
            if settings_device.get_SN() == device.get_SN():
                return True
        return False

    def in_storage(self, device: ICom):
        connections = self.bb.device_storage.get_connections()
        for connection in connections:
            settings_device = IComFactory.create_com(connection)
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

        # If the device is not in the settings list it has probably been closed so lets not do anything
        if not self.in_settings(self.device) and not self.in_storage(self.device):
            logger.info("Device is not in settings or storage, skipping")
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
                # Log connection failure with ping test for solarman devices
                if isinstance(self.device, ModbusSolarman):
                    self.diagnostic_logger.log_connection_failure(
                        self.device,
                        "Initial connection failed",
                        f"Device config: {self.device.get_config()}"
                    )

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

                    # Log device not found with ping test for solarman devices
                    if isinstance(self.device, ModbusSolarman):
                        self.diagnostic_logger.log_connection_failure(
                            self.device,
                            "Device not found on network",
                            f"Rescanning in 5 minutes. Config: {self.device.get_config()}"
                        )

                    self.time = event_time + 60000 * 5

            return self

        except Exception as e:
            logger.exception("Exception opening a device: %s", e)

            # Log exception with ping test for solarman devices
            if isinstance(self.device, ModbusSolarman):
                self.diagnostic_logger.log_connection_failure(
                    self.device,
                    f"Exception during connection: {type(e).__name__}",
                    f"Exception details: {str(e)}"
                )

            self.time = event_time + 10000
            return self
