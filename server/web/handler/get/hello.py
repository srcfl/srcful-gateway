import json
from ..handler import GetHandler
from ..requestData import RequestData


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns a simple hello world message",
            "returns": {"message": "hello world from srcful!"},
        }

    def do_get(self, request_data: RequestData):
        ret = self.schema()["returns"]

        return 200, json.dumps(ret)
