import json
from server.network import wifi
from server.tasks.initializeTask import InitializeTask

from ..handler import PostHandler
from ..requestData import RequestData

import logging

logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "Initialize the wallet to the gateway, if there is no internet the idAndWallet and signature will be returned a client can then use this message to initialize in the backend",
            "required": {"wallet": "string, wallet public key"},
            "optional": {"dry_run": "boolean, if true, all messages are sent to the backend but the wallet is not initialized"},
            "returns": {"initialized": "optional boolean, true if the wallet is initialized",
                        "idAndWallet": "optional string, gateway id and wallet public key as id:wallet",
                        "signature": "optional string, signature of the message in hex format"},
        }

    def json_schema(self):
        return json.dumps(self.schema())

    def do_post(self, data: RequestData):
        if "wallet" in data.data:

            dry_run = not ("dry_run" not in data.data or not data.data["dry_run"])

            t = InitializeTask(0, {}, data.data["wallet"], dry_run)
            if wifi.is_connected(): # this is actually if the network is available
                t.execute(0)
                if t.got_error is True:
                    return 500, json.dumps({"status": "error"})
                return 200, json.dumps({"initialized": t.is_initialized})
            else:
                id_and_wallet, sign, _ = t.get_id_and_wallet()
                return 200, json.dumps({"idAndWallet": id_and_wallet, "signature": sign})
            
        else:
            return 400, json.dumps({"status": "error", "message": "Invalid JSON or missing wallet"})
