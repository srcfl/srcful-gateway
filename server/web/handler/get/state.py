import json
from ..handler import GetHandler
from ..requestData import RequestData


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns the full state of the gateway",
            "returns": "state of the gateway as a json object",
        }

    def do_get(self, data: RequestData):

        return 200, json.dumps(data.bb.state)
