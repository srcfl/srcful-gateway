from ..handler import DeleteHandler
from ..requestData import RequestData
import json
import server.network.wifi as wifi

class Handler(DeleteHandler):
    def schema(self) -> dict:
        return self.create_schema(
            "Delete the wifi connections",
            returns={
                "status": "ok/error",
                "message": "optionalerror message",
            },
        )
    
    def do_delete(self, data: RequestData):
        try:
            wifi.delete_wifi_connections()
            return 200, json.dumps({"status": "ok"})
        except Exception as e:
            return 500, json.dumps({"status": "error", "message": str(e)})