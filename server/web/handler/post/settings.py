import json
import logging

from ..handler import PostHandler
from ..requestData import RequestData
from server.settings import Settings

log = logging.getLogger(__name__)

class Handler(PostHandler):
    def schema(self) -> dict:
        return self.create_schema(
            "Update application settings",
            required={
                Settings().SETTINGS: {
                    Settings.Harvest().HARVEST: {
                        Settings.Harvest().ENDPOINTS:
                            "List of URL endpoints the harvest data will be sent to"
                    }
                }
            },
            returns={
                "success": "Boolean indicating whether the update was successful"
            }
        )

    def do_post(self, data: RequestData):
        try:
            log.info(f"Received settings update: {data.data}")
            data.bb.settings.from_json(json.dumps(data.data))
            return 200, json.dumps({"success": True})
        except json.JSONDecodeError as e:
            log.error(f"Invalid JSON in request body: {str(e)}")
            return 400, json.dumps({"error": f"Invalid JSON format: {str(e)}"})
        except AttributeError as e:
            log.error(f"Error accessing or updating settings: {str(e)}")
            return 500, json.dumps({"error": f"Internal server error: {str(e)}"})
        except Exception as e:
            log.error(f"Unexpected error in SettingsHandler: {str(e)}")
            return 500, json.dumps({"error": f"Internal server error: {str(e)}"})