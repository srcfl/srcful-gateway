import json
from ..handler import GetHandler
from ..requestData import RequestData

class ListHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns a list of available message ids",
            "returns": {"ids": [1, 2, 3, 4, 5]}
        }

    def do_get(self, data: RequestData):
        ids = [m.id for m in data.bb.messages]
        return 200, json.dumps({"ids": ids})
    
class MessageHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns a message by id",
            "parameters": {"id": "int"},
            "returns": {"message": "string",
                        "type": "string (error, warning, info)",
                        "timestamp": "int (unix timestamp in seconds)",
                        "id": "int"}
        }

    def do_get(self, data: RequestData):
        try:
            id = int(data.post_params["id"])
            messages = data.bb.messages
            for m in messages:
                if m.id == id:
                    ret = {
                        "message": m.message,
                        "type": m.type.value,
                        "timestamp": m.timestamp,
                        "id": m.id
                    }
                    return 200, json.dumps(ret)
            return 404, json.dumps({"message": f"message {id} not found"})
        except Exception as e:
            return 400, json.dumps({"error": str(e)})