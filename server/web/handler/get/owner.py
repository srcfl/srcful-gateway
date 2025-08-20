import json
from server.tasks.getOwnerTask import GetOwnerTask

from ..handler import GetHandler

from ..requestData import RequestData


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns the owner wallet address of the gateway fetched from the backend",
            "returns": {"wallet": "string, wallet address of the gateway owner"},
        }

    def do_get(self, data: RequestData):
        # this works as the web response task is threaded in itself and will not block
        # the task queue execution - afaik :P
        t = GetOwnerTask(0, {})
        t.execute(0)

        if t.wallet is None:
            # Then the output can also be {"exception": "'Response' object has no attribute 'status'", "endpoint": "/api/owner"} 
            # If the gateway is offline and can not reach the endpoint
            # So we need to return a 504 error
            return t.reply.status_code, json.dumps({"body": t.reply.body})

        return 200, json.dumps({"wallet": t.wallet})
