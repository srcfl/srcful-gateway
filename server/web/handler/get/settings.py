import json
import logging

from ..handler import GetHandler
from ..requestData import RequestData
from server.app.settings.settings import Settings

log = logging.getLogger(__name__)

class Handler(GetHandler):
    def schema(self) -> dict:
        return self.create_schema(
            "Get application settings",
            returns={
                Settings().SETTINGS: {
                    Settings.Harvest().HARVEST: {
                        Settings.Harvest().ENDPOINTS:
                            "List of URL endpoints the harvest data will be sent to"
                    }
                }
            }
        )

    def do_get(self, data: RequestData):
        try:
            settings = data.bb.settings
            return 200, settings.to_json()
        except AttributeError as e:
            log.error(f"Error accessing settings: {str(e)}")
            return 500, json.dumps({"error": f"Internal server error {str(e)}"})
        except Exception as e:
            log.error(f"Unexpected error in SettingsHandler: {str(e)}")
            return 500, json.dumps({"error": f"Internal server error {str(e)}"})