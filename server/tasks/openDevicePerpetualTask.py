import logging
from server.blackboard import BlackBoard
from server.web.handler.get.network import ModbusScanHandler
from .task import Task
from server.inverters.ICom import ICom

logger = logging.getLogger(__name__)

class DevicePerpetualTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, device: ICom):
        super().__init__(event_time, bb)
        self.device = device
        self.scanner = ModbusScanHandler()

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
                # terminate and remove all devices from the blackboard
                logger.debug("Removing all devices from the blackboard after opening a new device")
                for i in self.bb.devices.lst:
                    i.disconnect()
                    self.bb.devices.remove(i)

                self.bb.devices.add(self.device)
                self.bb.add_info("Inverter opened: " + str(self.device.get_config()))
                return
            
            else:
                port = self.device.get_config()['port'] # get the port from the previous inverter config
                hosts = self.scanner.scan_ports([int(port)], 0.01) # overwrite hosts with the new result of the scan
                
                if len(hosts) > 0:
                    # At least one device was found on the port
                    self.device = self.device.clone(hosts[0]['ip'])
                    logger.info("Found inverter at %s, retry in 5 seconds...", hosts[0]['ip']) 
                    self.time = event_time + 5000
                else:
                    # possibly we should create a new device object. We have previously had trouble with reconnecting in the Harvester
                    message = "Failed to open inverter, retry in 5 minutes: " + str(self.device.get_config())
                    logger.info(message)
                    self.bb.add_error(message)
                    self.time = event_time + 60000 * 5

            return self
        
        except Exception as e:
            logger.exception("Exception opening inverter: %s", e)
            self.time = event_time + 10000
            return self