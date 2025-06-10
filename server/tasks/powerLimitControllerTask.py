import logging
from typing import List, Union
from server.app.blackboard import BlackBoard
from server.devices.Device import Device, DeviceMode, DeviceCommand, DeviceCommandType
from server.tasks.harvest import Harvest
from server.tasks.harvestTransport import DefaultHarvestTransportFactory
from server.tasks.itask import ITask
from .harvestableTask import HarvestableTask

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PowerLimitControllerTask(HarvestableTask):
    def __init__(self, event_time: int, bb: BlackBoard, device: Device):
        super().__init__(event_time, bb, device)
        self.is_initialized = False

    def execute(self, event_time) -> Union[List[ITask], ITask, None]:
        start_time = event_time

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

        # harvest data (in control mode we do not want the mega harvest)
        harvest = self.collect_harvest_data(start_time, force_verbose=False)
        elapsed_time_ms = self.bb.time_ms() - start_time

        # TODO: check fuse protection

        if self.is_initialized:
            while self.device.has_commands():
                command:DeviceCommand = self.device.pop_command() # pop each command from the device
                if command.command_type == DeviceCommandType.SET_BATTERY_POWER:
                    self.device.profile.set_battery_power(self.device, command.values[0])

        # deinit check here
        if self.device.get_mode() == DeviceMode.READ:
            #if self.is_initialized:
            if self.device.profile.deinit_device(self.device):
                logging.info(f"Successfully deinitialized device {self.device.get_SN()}")
                self.is_initialized = False
            else:
                logging.error(f"Failed to deinitialize device {self.device.get_SN()}")

            logging.info(f"Device {self.device.get_SN()} is in read mode, go to harvest")

            # Create final transport before switching to harvest mode
            transports = self.create_final_transport(event_time, self.bb.settings.harvest.endpoints)
            harvest_task = Harvest(event_time, self.bb, self.device, DefaultHarvestTransportFactory())
            
            return [harvest_task] + transports

        # Check if it's time to transport the harvest
        transport = self._create_transport(self.bb.time_ms() + elapsed_time_ms * 2, self.bb.settings.harvest.endpoints)
        
        self.time = self.bb.time_ms() + 500
        
        if len(transport) > 0:
            return [self] + transport
        return self
