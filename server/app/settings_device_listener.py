import logging
from server.app.blackboard import BlackBoard, ChangeSource
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.devices.IComFactory import IComFactory
from server.app.settings.settings import DebouncedMonitorBase
from server.app.settings.settings_observable import ChangeSource

logger = logging.getLogger(__name__)

class SettingsDeviceListener(DebouncedMonitorBase):
        def __init__(self, blackboard: BlackBoard, debounce_delay: float = 0.5):
            super().__init__(debounce_delay)
            self.blackboard = blackboard

        def _perform_action(self, source: ChangeSource):

            settings_modified = False

            # we do nothing if the change is local
            if source == ChangeSource.LOCAL:
                return
            
            for connection in self.blackboard.settings.devices.connections:
                
                try:
                    com = IComFactory.create_com(connection)
                except ValueError as e:
                    logger.error("Error creating ICom object for connection: %s, removing it from the settings", e)
                    self.blackboard.settings.devices.connections.remove(connection)
                    settings_modified = True
                    continue

                # check if we have a new format
                if com.get_config() != connection:
                    logger.info("Device %s has a new format, updating the settings", com.get_SN())
                    connection.clear()
                    connection.update(com.get_config())
                    settings_modified = True
                if self.blackboard.devices.find_sn(com.get_SN()) is None:
                    logger.info("Device %s from settings was not found in the blackboard devices, opening a perpetual task to connect it", com.get_SN())
                    self.blackboard.add_task(DevicePerpetualTask(self.blackboard.time_ms(), self.blackboard, com))
                else:
                    logger.info("Device %s from settings was found in the blackboard devices, skipping", com.get_SN())


            if settings_modified:
                self.blackboard.settings.devices.notify_listeners(ChangeSource.LOCAL)
