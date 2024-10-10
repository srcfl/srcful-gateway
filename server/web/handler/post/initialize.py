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
            "optional": {"dry_run": "boolean, if true, all messages are sent to the backend but the wallet is not initialized"},
            "returns": {"initialized": "boolean, true if the wallet is initialized"},
        }

    def json_schema(self):
        return json.dumps(self.schema())

    def do_post(self, data: RequestData):
        if "wallet" in data.data:

            dry_run = not ("dry_run" not in data.data or not data.data["dry_run"])

            t = InitializeTask(0, {}, data.data["wallet"], dry_run)
            t.execute(0)

            if t.is_initialized is None:
                return t.reply.status_code, json.dumps({"body": t.reply.body})

            return 200, json.dumps({"initialized": t.is_initialized})
        else:
            return 400, json.dumps({"status": "bad request"})
