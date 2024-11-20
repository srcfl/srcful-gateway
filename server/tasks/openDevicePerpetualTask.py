import logging
from typing import Optional
from server.app.blackboard import BlackBoard
from server.devices.IComFactory import IComFactory
from server.app.settings.settings_observable import ChangeSource
from .task import Task
from server.devices.ICom import ICom
from server.network.network_utils import NetworkUtils


logger = logging.getLogger(__name__)

class DevicePerpetualTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device: ICom):
        super().__init__(event_time, bb)
        self.device:ICom = device
        self.old_device: Optional[ICom] = None


    def in_settings(self, device: ICom):
        for settings in self.bb.settings.devices.connections:
            settings_device = IComFactory.create_com(settings)
            if settings_device.get_SN() == self.device.get_SN():
                return True
        return False

    def execute(self, event_time):
        logger.info("*************************************************************")
        logger.info("******************** DevicePerpetualTask ********************")
        logger.info("*************************************************************")
        
        # Check if the device is already in the blackboard and is open
        # If it is, we don't need to do anything. This check is necessary to ensure 
        # that a device does not get opened multiple times.
        existing_device = self.bb.devices.find_sn(self.device.get_SN())
        if existing_device and existing_device.is_open():
            return None
        
        # If the device is not in the settings list it has probably been closed so lets not do anything
        if not self.in_settings(self.device):
            return None
        
        try:
            if self.device.connect():
                
                if self.bb.devices.contains(self.device) and not self.device.is_open():
                    message = "Device is already in the blackboard, no action needed"
                    logger.error(message)
                    self.bb.add_error(message)
                    return None

                message = "Device opened: " + str(self.device.get_config())
                logger.info(message)

                if self.old_device:
                    self.bb.settings.devices.remove_connection(self.old_device, ChangeSource.LOCAL)
                
                self.bb.devices.add(self.device)
                self.bb.add_info(message)
                return None
            
            else:
                
                if self.old_device:
                    logger.info("Device not found in two steps, giving up the perpetual task: %s, %s", self.old_device.get_SN(), self.device.get_SN())
                    logger.info("Removing device from settings: %s", self.old_device.get_SN())
                    self.bb.settings.devices.remove_connection(self.old_device, ChangeSource.LOCAL)

                tmp_device = self.device.find_device() # find the device on the network
                
                if tmp_device is not None:

                    self.old_device = self.device
                    self.device = tmp_device
                    logger.info("Found a device at %s, retry in 5 seconds...", self.device.get_config())
                    self.time = event_time + 5000
                    self.bb.add_info("Found a device at " + self.device.get_name() + ", retry in 5 seconds...")
                else:
                    message = "Failed to find %s, rescan and retry in 5 minutes", self.device.get_SN()
                    logger.info(message)
                    self.bb.add_error(message)
                    self.time = event_time + 60000 * 5
                    
            return self
        
        except Exception as e:
            logger.exception("Exception opening a device: %s", e)
            self.time = event_time + 10000
            return self