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

    def do_get(self, request_data: RequestData):
        # this works as the web response task is threaded in itself and will not block
        # the task queue execution - afaik :P
        t = GetNameTask(0, {})
        t.execute(0)
        t.t.join()
        t.execute(0)

        if t.name is None:
            return t.response.status, json.dumps({"body": t.response.body})

        return 200, json.dumps({"name": t.name})
