from server.blackboard import BlackBoard
from server.settings import Settings
from .configurationMutationTask import ConfigurationMutationTask

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SaveStateTask(ConfigurationMutationTask):
    SUBKEY = "state"
    def __init__(self, event_time: int, bb: BlackBoard):
        self.state = bb.state
        super().__init__(event_time, bb, self.SUBKEY, self.state)
        logger.info("State: %s", self.state)


    def _on_200(self, reply):
        super()._on_200(reply)


    def _on_error(self, reply):
        logger.error("Failed to save state %s", reply)
        logger.error("State: %s", self.state)
        super()._on_error(reply)
        self.state = self.bb.state
        return 60000
    
    
class SaveStatePerpetualTask(SaveStateTask  ):
    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)

    def _on_200(self, reply):
        super()._on_200(reply)
        self.time = self.time + 1000 * 60 * 5 # 5 minutes
        return self

    def _on_error(self, reply):
        super()._on_error(reply)
        logger.error("Failed to save state %s", reply)
        logger.error("State: %s", self.state)
        logger.warning("Failed to save state %s", reply)
        self.state = self.bb.state
        return 1000 * 10 # Retry after 10 seconds