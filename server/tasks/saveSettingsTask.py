from server.app.blackboard import BlackBoard
from server.app.settings import Settings
from .configurationMutationTask import ConfigurationMutationTask

class SaveSettingsTask(ConfigurationMutationTask):
    def __init__(self, event_time: int, bb: BlackBoard, settings: Settings = None):
        self.settings = settings if settings is not None else bb.settings
        super().__init__(event_time, bb, bb.settings.API_SUBKEY, self.settings.to_dict())

    def _on_200(self, reply):
        super()._on_200(reply)


    def _on_error(self, reply):
        super()._on_error(reply)
        return 60000  # Retry after 1 minute