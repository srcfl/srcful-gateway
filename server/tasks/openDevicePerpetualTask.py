import logging
from server.blackboard import BlackBoard
from .task import Task
from server.devices.ICom import ICom
from server.network.network_utils import NetworkUtils
from server.settings import ChangeSource


logger = logging.getLogger(__name__)

class DevicePerpetualTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device: ICom):
        super().__init__(event_time, bb)
        self.device = device

    def execute(self, event_time):
        logger.info("*************************************************************")
        logger.info("******************** DevicePerpetualTask ********************")
        logger.info("*************************************************************")
        
        try:
            if self.device.connect():
                
                if not self.device.is_valid():
                    self.device.disconnect()
                    message = "Failed to open device: " + str(self.device.get_config())
                    logger.error(message)
                    self.bb.add_error(message)
                    return None
                
                if self.bb.devices.contains(self.device):
                    message = "Device is already in the blackboard, no action needed"
                    logger.error(message)
                    self.bb.add_error(message)
                    return None

                message = "Device opened: " + str(self.device.get_config())
                logger.info(message)

                # self.bb.devices.remove_by_mac(self.device.get_config()[NetworkUtils.MAC_KEY], ChangeSource.LOCAL)
                self.bb.devices.add(self.device)
                self.bb.add_info(message)
                return None
            
            else:
                
                tmp_device = self.device.find_device() # find the device on the network
                
                if tmp_device is not None:
                    self.device = tmp_device
                    logger.info("Found a device at %s, retry in 5 seconds...", self.device.get_config()[NetworkUtils.IP_KEY])
                    self.time = event_time + 5000
                    self.bb.add_info("Found a device at " + self.device.get_config()[NetworkUtils.IP_KEY] + ", retry in 5 seconds...")
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