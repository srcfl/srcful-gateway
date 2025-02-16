import json

from ..handler import GetHandler

from ..requestData import RequestData


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Get the gateway uptime in milliseconds",
            "returns": {"msek": "int, milliseconds since boot"},
        }

    def do_get(self, data: RequestData):
        return 200, json.dumps(
            {"msek": data.bb.elapsed_time()}
        )
