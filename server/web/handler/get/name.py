import json
from server.tasks.getNameTask import GetNameTask

from ..handler import GetHandler

from ..requestData import RequestData


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns the name of the gateway fetched from the backend",
            "returns": {"name": "string, name of the gateway"},
        }

    def do_get(self, data: RequestData):
        # this works as the web response task is threaded in itself and will not block
        # the task queue execution - afaik :P
        t = GetNameTask(0, {})
        t.execute(0)

        if t.name is None:
            # Then the output can also be {"exception": "'Response' object has no attribute 'status'", "endpoint": "/api/name"} 
            # If the gateway is offline and can not reach the endpoint
            # So we need to return a 504 error
            if hasattr(t.reply, 'status'):
                return t.reply.status, json.dumps({"body": t.reply.body})
            else:
                return 504, json.dumps({"body": t.reply})

        return 200, json.dumps({"name": t.name})
