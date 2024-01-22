import json
from ..handler import GetHandler

from ..requestData import RequestData


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns the configuration of the running inverter, details depend on the inverter type.",
            "returns": {
                "connection": "string, connection type (TCP, RTU)",
                "type": "string, inverter type (solaredge, huawei, ...)",
                "host": "string, inverter TCP ip address",
                "port": "int, inverter TCP port",
                "status": "string, open, closed or No inverter",
            },
        }

    def do_get(self, request_data: RequestData):
        config = {"status": "No inverter"}

        if len(request_data.bb.inverters.lst) > 0:
            inverter = request_data.bb.inverters.lst[0]
            config = inverter.get_config_dict()

            if inverter.is_open():
                config["status"] = "open"
            else:
                config["status"] = "closed"

        return 200, json.dumps(config)
