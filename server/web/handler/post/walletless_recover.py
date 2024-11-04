import json
from server.tasks.walletlessRecoverTask import WalletlessRecoverTask

from ..handler import PostHandler
from ..requestData import RequestData

import logging

logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "initialize the wallet",
            "required": {"api_key": "string, recovery api key",
                         "access_key": "string, recovery access key"},
            "returns": {"prv": "string the private key",
                        "pub": "string the public key"},
        }

    def json_schema(self):
        return json.dumps(self.schema())

    def do_post(self, data: RequestData):
        if "wallet" in data.data:

            t = WalletlessRecoverTask(0, {}, data.data["api_key"], data.data["access_key"])
            t.execute(0)

            if len(t.prv) == 0 or len(t.pub) == 0:
                return t.reply.status_code, json.dumps({"body": t.reply.body})

            return 200, json.dumps({"prv": t.prv, "pub": t.pub})
        else:
            return 400, json.dumps({"status": "bad request"})
