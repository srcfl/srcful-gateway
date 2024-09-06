from server.blackboard import BlackBoard
from server.settings import Settings
from .configurationMutationTask import ConfigurationMutationTask

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SaveStateTask(ConfigurationMutationTask):
    SUBKEY = "state"
    def __init__(self, event_time: int, bb: BlackBoard, state: dict = None):
        self.state = state if state is not None else bb.state
        super().__init__(event_time, bb, self.SUBKEY, self.state)

    def _on_200(self, reply):
        super()._on_200(reply)
        if self.is_saved:
            self.bb.add_info("State saved successfully")
        else:
            self.bb.add_warning("Failed to save state")

    def _on_error(self, reply):
        super()._on_error(reply)
        self.bb.add_error("Error saving state")
        return 60000
    
    
class SaveStatePerpetualTask(SaveStateTask  ):
    def __init__(self, event_time: int, bb: BlackBoard, state: dict = None):
        super().__init__(event_time, bb, state)

    def _on_200(self, reply):
        super()._on_200(reply)
        self.time = self.time + 1000 * 60 * 5 # 5 minutes
        return self

    def _on_error(self, reply):
        super()._on_error(reply)
        logger.warning("Failed to save state %s", reply)
        return 1000 * 10 # Retry after 10 seconds