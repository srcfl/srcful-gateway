import json
from ..handler import GetHandler
from ..requestData import RequestData
from server.tasks.saveStateTask import SaveStateTask


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns the full state of the gateway",
            "returns": "state of the gateway as a json object",
        }

    def do_get(self, data: RequestData):

        return 200, json.dumps(data.bb.state)
    
class UpdateStateHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns the full state of the gateway and updates the configuration state",
        }
    
    def do_get(self, data: RequestData):
        data.bb.add_task(SaveStateTask(data.bb.time_ms() + 100, data.bb))
        return 200, json.dumps(data.bb.state)