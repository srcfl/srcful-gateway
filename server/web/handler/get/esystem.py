import json
from ..handler import GetHandler

from ..requestData import RequestData



class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns the esystem configuration.",
            "returns": {
                "battery": "list of objects, like {\"sn\": \"string device sn\"}",
                "solar": "list of objects, like {\"sn\": \"string device sn\"}",
                "load": "list of objects, like {\"sn\": \"string device sn\"}",
                "grid": "list of objects, like {\"sn\": \"string device sn\"}",
            },
        }

    def do_get(self, data: RequestData):
        config = {"battery": [{"sn": sn} for sn in data.bb.esystem.battery_sn_list],
                  "solar": [{"sn": sn} for sn in data.bb.esystem.solar_sn_list],
                  "load": [{"sn": sn} for sn in data.bb.esystem.load_sn_list],
                  "grid": [{"sn": sn} for sn in data.bb.esystem.grid_sn_list]}

        return 200, json.dumps(config)