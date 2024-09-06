from server.blackboard import BlackBoard
from server.settings import Settings
from .configurationMutationTask import ConfigurationMutationTask

class SaveSettingsTask(ConfigurationMutationTask):
    def __init__(self, event_time: int, bb: BlackBoard, settings: Settings = None):
        self.settings = settings if settings is not None else bb.settings
        super().__init__(event_time, bb, bb.settings.API_SUBKEY, self.settings.to_dict())

    def _on_200(self, reply):
        super()._on_200(reply)
        if self.is_saved:
            self.bb.add_info("Settings saved successfully")
        else:
            self.bb.add_warning("Failed to save settings")

    def _on_error(self, reply):
        super()._on_error(reply)
        self.bb.add_error("Error saving settings")
        return 60000  # Retry after 1 minute