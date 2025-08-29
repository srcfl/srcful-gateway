# a simple echo endpoint that returns the data it received

import json

from ..handler import PostHandler
from ..requestData import RequestData


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "Adds a new endpoint",
            "returns": {"status": "string, the status of the operation"},
        }

    def do_post(self, data: RequestData):
        
        endpoint: str = data.data.get("endpoint")
        
        data.bb.add_endpoint(endpoint)

        return 200, json.dumps({"status": "success"})
