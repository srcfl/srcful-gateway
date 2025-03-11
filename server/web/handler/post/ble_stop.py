# a simple echo endpoint that returns the data it received

import json

from ..handler import PostHandler
from ..requestData import RequestData


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "Signals the BLE to stop, this is not used on the Blixt gateway, ble will stop advertising after a few minutes after activation but will not stop technically",
            "returns": {"status": "sucess", "messsage": "BLE advertising scheduled to stop"},
        }

    def do_post(self, data: RequestData):
        return 200, json.dumps({"status": "success", "message": "BLE advertising scheduled to stop"})
