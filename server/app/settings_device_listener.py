import logging
from server.app.blackboard import BlackBoard, ChangeSource
from server.network.network_utils import NetworkUtils
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.devices.IComFactory import IComFactory
from server.app.settings import DebouncedMonitorBase, ChangeSource

logger = logging.getLogger(__name__)

class SettingsDeviceListener(DebouncedMonitorBase):
        def __init__(self, blackboard: BlackBoard, debounce_delay: float = 0.5):
            super().__init__(debounce_delay)
            self.blackboard = blackboard

        def _perform_action(self, source: ChangeSource):

            # we do nothing if the change is local
            if source == ChangeSource.LOCAL:
                return
            
            for connection in self.blackboard.settings.devices.connections:
                
                com = IComFactory.create_com(connection)
                
                # always update the config in the settings
                # clear the dict and update it with the new config
                connection.clear()
                connection.update(com.get_config())

                for device in self.blackboard.devices.lst:
                    
                    # Check if the device already exists in the blackboard
                    # Then check if the device is open, if not, then start a perpetual task to open it
                    # TODO: This might start another DevicePerpetualTask in addition to one that might
                    # already be running from the blackboard. Consider reworking this logic
                    # if device.get_SN() == com.get_SN():
                    #     # update the settings connez
                    #     if not device.is_open():
                    #         logger.info("Device %s from settings was found in the blackboard, but not open", com.get_SN())
                    #         logger.info("Removing %s from the blackboard and opening a perpetual task to connect it", com.get_SN())
                    #         self.blackboard.devices.remove(device)
                    #         self.blackboard.add_task(DevicePerpetualTask(self.blackboard.time_ms(), self.blackboard, IComFactory.create_com(connection)))
                    #     break
                # else:
                    # Device not found in the blackboard, but apperantly exists in the settings,
                    # which means it was previously connected So we try to open it again
                    if device.get_SN() != com.get_SN():
                        logger.info("Device %s from settings was not found in the blackboard devices, opening a perpetual task to connect it", com.get_SN())
                        self.blackboard.add_task(DevicePerpetualTask(self.blackboard.time_ms(), self.blackboard, IComFactory.create_com(connection)))
                    else:
                        logger.info("Device %s from settings was found in the blackboard devices, skipping", com.get_SN())
                        
