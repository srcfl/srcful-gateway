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

    def do_get(self, data: RequestData):
        config = {"status": "No inverter"}

        if len(data.bb.devices.lst) > 0:
            der = data.bb.devices.lst[0]
            config = der.get_config()

            if der.is_open():
                config["status"] = "open"
            else:
                config["status"] = "closed"

        return 200, json.dumps(config)
