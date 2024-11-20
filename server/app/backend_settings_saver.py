from server.app.settings.settings import DebouncedMonitorBase
from server.app.settings.settings_observable import ChangeSource

from server.app.blackboard import BlackBoard
from server.tasks.saveSettingsTask import SaveSettingsTask
import logging

logger = logging.getLogger(__name__)

class BackendSettingsSaver(DebouncedMonitorBase):
    """ Monitors settings changes and schedules a save to the backend, ignores changes from the backend """
    def __init__(self, blackboard: BlackBoard, debounce_delay: float = 0.5):
        super().__init__(debounce_delay)
        self.blackboard = blackboard

    def _perform_action(self, source: ChangeSource):
        if source != ChangeSource.BACKEND:
            logger.info("Settings change detected, scheduling a save to backend")
            self.blackboard.add_task(SaveSettingsTask(self.blackboard.time_ms() + 500, self.blackboard))
        else:  
            logger.info("No need to save settings to backend as the source is the backend")