from server.app.blackboard import BlackBoard
from .configurationMutationTask import ConfigurationMutationTask
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SaveDeviceConfigurationTask(ConfigurationMutationTask):
    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb, "devices", {"devices": bb.settings.devices.connections})

    def _on_200(self, reply):
        super()._on_200(reply)
        logger.info("Device configurations saved to backend: %s", self.bb.settings.devices.connections)
        self.time = self.bb.time_ms() + 1000 * 60 * 60 * 6  # Run again after 6 hours
        return self

    def _on_error(self, reply):
        super()._on_error(reply)
        logger.error("Error saving device configurations to backend: %s", reply)
        return 1000 * 10  # Retry after 10 seconds
