import json
import logging

from server.network.scan import WifiScanner

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
        s = WifiScanner()
        s.delete_all()
        
        return 404, json.dumps({"device not found: ": id})