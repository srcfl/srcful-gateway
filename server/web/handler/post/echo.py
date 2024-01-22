# a simple echo endpoint that returns the data it received

import json

from ..handler import PostHandler
from ..requestData import RequestData


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "Returns the data it received",
            "returns": {"echo": "string, the data it received"},
        }

    def do_post(self, request_data: RequestData):
        ret = {"echo": request_data.data}

        return 200, json.dumps(ret)
