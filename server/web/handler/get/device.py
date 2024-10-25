import json
from ..handler import GetHandler

from ..requestData import RequestData


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns the configuration of the running devices, details depend on the device type.",
            "returns": [{
                "connection": "string, connection type (TCP, RTU, SOLARMAN, P1TELNET)",
                "status": "string, open, closed or No inverter",
                "id": "unique id of the device",
                "config": "dict, device specific configuration",
            
            }],
        }

    def do_get(self, data: RequestData):
        configs = []

        for device in data.bb.devices.lst:
            config = device.get_config()

            if device.is_open():
                config["status"] = "open"
            else:
                config["status"] = "closed"

            config["id"] = device.get_SN()
            configs.append(config)
            

        return 200, json.dumps(configs)
