import logging
from server.blackboard import BlackBoard
from .task import Task
from server.inverters.ICom import ICom
from server.network.network_utils import NetworkUtils

logger = logging.getLogger(__name__)

class DevicePerpetualTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device: ICom):
        super().__init__(event_time, bb)
        self.device = device

    def execute(self, event_time):
        
        # has a device been opened? This is needed as some other task may open a device before this task is executed
        if len(self.bb.devices.lst) > 0 and self.bb.devices.lst[0].is_open():
            logger.debug("A device is already open, removing self.device from the blackboard")
            self.bb.devices.remove(self.device)
            if self.device.is_open():
                self.device.disconnect()
            return
        try:
            if self.device.connect():
                
                if not self.device.is_valid():
                    self.device.disconnect()
                    message = "Failed to open device: " + str(self.device.get_config())
                    logger.error(message)
                    self.bb.add_error(message)
                    return None
                
                # terminate and remove all devices from the blackboard
                logger.debug("Removing all devices from the blackboard after opening a new device")
                for i in self.bb.devices.lst:
                    i.disconnect()
                    self.bb.devices.remove(i)

                self.bb.devices.add(self.device)
                self.bb.add_info("Device opened: " + str(self.device.get_config()))
                return None
            
            else:
                self.device = self.device.find_device() # find the device on the network
                
                if self.device is not None:
                    logger.info("Found a device at %s, retry in 5 seconds...", self.device.get_config()[NetworkUtils.IP_KEY])
                    self.time = event_time + 5000
                    self.bb.add_info("Found a device at " + self.device.get_config()[NetworkUtils.IP_KEY] + ", retry in 5 seconds...")
                else:
                    message = "Failed to find a device, rescan and retry in 5 minutes"
                    logger.info(message)
                    self.bb.add_error(message)
                    self.time = event_time + 60000 * 5
                    
            return self
        
        except Exception as e:
            logger.exception("Exception opening a device: %s", e)
            self.time = event_time + 10000
            return self