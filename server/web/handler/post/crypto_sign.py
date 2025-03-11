import datetime
import json
import random
import re
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
                "description": "Create a signed message with nonce, timestamp and gateway serial number",
                "optional": {"message": "string, a message to sign should not contain | characters.",
                             "timestamp": "string, a timestamp in UTC Y-m-dTH:M:SZ format. if not provided, the device current time will be used."},
                "returns": {"message": "message|nonce|timestamp (UTC Y-m-dTH:M:SZ)|serial",
                            "sign": "the signature of the message in hex format"},
                }

    def json_schema(self):
        return json.dumps(self.schema())

    def _construct_message(self, message: Optional[str], timestamp: Optional[str]) -> str:
        if message is None:
            message = ""
        else:
            if "|" in message:
                raise ValueError("message cannot contain | characters")

            message += "|"

        
        nonce = str(random.randint(0, 1000000)) 
        message += nonce + "|"
        if timestamp is None:
            timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            # check if timestamp is in UTC Y-m-dTH:M:SZ format
            if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', timestamp):
                raise ValueError("timestamp must be in UTC Y-m-dTH:M:SZ format")
        message += timestamp + "|"

        return message


    def _add_serial_and_sign_message(self, message: str, chip: crypto.Chip) -> tuple[str, str]:
        serial = chip.get_serial_number().hex()
        message += serial
        return message, chip.get_signature(message).hex()


    def do_post(self, data: RequestData):
        try:
            message = self._construct_message(data.data.get("message"), data.data.get("timestamp"))
        except ValueError as e:
            return 400, json.dumps({"status": str(e)})


        with crypto.Chip() as chip:
            message, signature = self._add_serial_and_sign_message(message, chip)

            return 200, json.dumps({"message": message, "sign": signature})

