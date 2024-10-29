from ..handler import DeleteHandler
from ..requestData import RequestData
import json

class Handler(DeleteHandler):
    def schema(self) -> dict:
        return self.create_schema(
            "Delete a message by id",
            required={"id": "int"},
            returns={
                "id": "id ",
            },
        )
    
    def do_delete(self, data: RequestData):
        if "id" not in data.post_params:
            return 400, json.dumps({"status": "bad request", "schema": self.schema()})
        
        id = data.post_params["id"]

        for device in data.bb.devices.lst:
            if device.get_SN() == id:
                device.disconnect()
                data.bb.devices.remove(device)
                return 200, json.dumps({"Disconnected device with id": id})

        
        return 404, json.dumps({"device not found: ": id})