from ..handler import DeleteHandler
from ..requestData import RequestData
import json


class Handler(DeleteHandler):
    def schema(self) -> dict:
        return self.create_schema(
            "Delete the modbus device and return the device config",
            returns= {
                "device": "dict, the device that was deleted",
            },
        )

    def do_delete(self, data: RequestData):
        if len(data.bb._devices.lst) > 0:
            device = data.bb._devices.lst[0]
            device.disconnect()
            data.bb._devices.remove(device)

            conf = device.get_config()
            conf["is_open"] = device.is_open()
            
            data = {"device": conf}

            return 200, json.dumps(data)

        return 400, json.dumps({"error": "no modbus device initialized"})
