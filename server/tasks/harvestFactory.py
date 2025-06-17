from server.app.blackboard import BlackBoard
from server.devices.ICom import ICom
from .deviceTask import DeviceTask
from .harvestTransport import DefaultHarvestTransportFactory
from server.app.settings import ChangeSource
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class HarvestFactory:
    """This class is responsible for creating harvest tasks when inverters are added to the blackboard."""

    def __init__(self, bb: BlackBoard):
        self.bb = bb
        bb.devices.add_listener(self)

    def add_device(self, com: ICom):
        """Add the device to the blackboard and create a harvest task and save it to the settings"""
        # Save the connection to persistent storage
        device_config = com.get_config()
        logger.debug(f"Attempting to save connection: {device_config}")

        if self.bb.storage.add_connection(device_config):
            logger.info(f"Connection saved for device {com.get_name()} : {com.get_SN()}")
        else:
            logger.warning(f"Failed to save connection for device {com.get_name()} : {com.get_SN()}")

        # Create device task and save to settings
        self.bb.add_task(DeviceTask(self.bb.time_ms() + 1000, self.bb, com, DefaultHarvestTransportFactory()))
        self.bb.settings.devices.add_connection(com, ChangeSource.LOCAL)
        logger.info(f"Added device {com.get_name()} : {com.get_SN()}")
        self.bb.add_info(f"Added device {com.get_name()} : {com.get_SN()}")

    def remove_device(self, device: ICom):
        """Disconnect the device and remove it from the blackboard settings"""
        try:
            device.disconnect()
        except ValueError:
            logger.warning("Device %s already disconnected", device)

        # Remove connection from persistent storage
        if self.bb.storage.remove_connection(device.get_SN()):
            logger.info(f"Connection removed from storage for device {device.get_name()} : {device.get_SN()}")
        else:
            logger.warning(f"Failed to remove connection from storage for device {device.get_name()} : {device.get_SN()}")

        self.bb.settings.devices.remove_connection(device, ChangeSource.LOCAL)
        logger.info(f"Removed device {device.get_name()} : {device.get_SN()}")
        self.bb.add_info(f"Removed device {device.get_name()} : {device.get_SN()}")
