import json
from ..handler import GetHandler

from ..requestData import RequestData
from server.wifi.wifi import get_connection_configs


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns the list of networks",
            "returns": {
                "connections": "list of dicts, containing the configured networks."
            },
        }

    def do_get(self, data: RequestData):
        return 200, json.dumps({"connections": get_connection_configs()})
