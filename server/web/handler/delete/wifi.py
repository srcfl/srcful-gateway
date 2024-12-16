import json
import logging

from server.network.wifi import WiFiHandler

from ..handler import DeleteHandler
from ..requestData import RequestData
import json

class Handler(DeleteHandler):
    def schema(self) -> dict:
        return self.create_schema(
            "Delete all wifi networks",
            returns={
                "status": "success or error message",
            },
        )
    
    def do_delete(self, data: RequestData):
        try:
            s = WiFiHandler("ssid", "psk")
            s.delete_connections()
        except Exception as e:
            return 500, json.dumps({"status": "error", "message": str(e)})
        
        return 404, json.dumps({"device not found: ": id})