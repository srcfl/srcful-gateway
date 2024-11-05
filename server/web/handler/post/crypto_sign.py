import datetime
import json
import random
from typing import Optional
from server.crypto import crypto

from ..handler import PostHandler
from ..requestData import RequestData

import logging

logger = logging.getLogger(__name__)


class Handler(PostHandler):

    def schema(self):
        return  {
                "type": "post",
                "description": "Recover the private and public keys for walletless signing",
                "optional": {"message": "string, a message to sign should not contain | characters."},
                "returns": {"message": "message|nonce|timestamp ( UTC Y-m-dTH:M:SZ)|serial",
                            "sign": "the signature of the message"},
                }

    def json_schema(self):
        return json.dumps(self.schema())

    def _construct_message(self, message: Optional[str]) -> str:
        if message is None:
            message = ""
        else:
            if "|" in message:
                raise ValueError("message cannot contain | characters")

            message += "|"

        
        nonce = str(random.randint(0, 1000000)) 
        message += nonce + "|"
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        message += timestamp + "|"

        return message


    def _add_serial_and_sign_message(self, message: str, chip: crypto.Chip) -> tuple[str, str]:
        serial = chip.get_serial_number().hex()
        message += serial
        return message, chip.get_signature(message).hex()


    def do_post(self, data: RequestData):
        try:
            message = self._construct_message(data.data.get("message"))
        except ValueError as e:
            return 400, json.dumps({"status": str(e)})


        with crypto.Chip() as chip:
            message, signature = self._add_serial_and_sign_message(message, chip)

            return 200, json.dumps({"message": message, "sign": signature})

