import json

from server.network.network_utils import NetworkUtils
from ..handler import DeleteHandler
from ..requestData import RequestData
import json


class Handler(DeleteHandler):
    def schema(self) -> dict:
        return self.create_schema(
            "Disconnect from WiFi",
            returns={
                "status": "Success or Error message",
                "message": "Success or Error message",
            },
        )

    def do_delete(self, data: RequestData):
        try:
            if NetworkUtils.disconnect_from_wifi():
                return 200, json.dumps({"status": "Success", "message": "Disconnected from WiFi"})
            else:
                return 500, json.dumps({"status": "Error", "message": "Failed to disconnect from WiFi"})
        except Exception:
            return 500, json.dumps({"status": "Error", "message": "Failed to disconnect from WiFi"})
