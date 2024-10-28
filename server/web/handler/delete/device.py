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
        id = data.post_params["id"]

        for device in data.bb.devices.lst:
            if device.get_SN() == id:
                device.terminate()
                return 200, json.dumps({"closed and deleted device with id": id})

        
        return 404, json.dumps({"device not found: ": id})