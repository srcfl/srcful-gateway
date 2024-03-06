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
        id = data.parameters["id"]
        if data.bb.delete_message(id):
            return 200, json.dumps({"id": id})
        else:
            return 404, json.dumps({"id": id})