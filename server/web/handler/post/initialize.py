import json
from server.tasks.initializeTask import InitializeTask

from ..handler import PostHandler
from ..requestData import RequestData

import logging

logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "initialize the wallet",
            "required": {"wallet": "string, wallet public key"},
            "returns": {"initialized": "boolean, true if the wallet is initialized"},
        }

    def json_schema(self):
        return json.dumps(self.schema())

    def do_post(self, request_data: RequestData):
        if "wallet" in request_data.data:
            t = InitializeTask(0, {}, request_data.data["wallet"])
            t.execute(0)
            t.t.join()
            t.execute(0)

            if t.is_initialized is None:
                return t.response.status, json.dumps({"body": t.response.body})

            return 200, json.dumps({"initialized": t.is_initialized})
        else:
            return 400, json.dumps({"status": "bad request"})
