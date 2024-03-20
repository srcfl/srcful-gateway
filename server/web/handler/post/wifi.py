import json
import logging

from server.wifi.wifi import WiFiHandler
from server.tasks.openWiFiConTask import OpenWiFiConTask

from ..handler import PostHandler
from ..requestData import RequestData


log = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "open a wifi connection",
            "required": {
                "ssid": "string, ssid of the wifi",
                "psk": "string, password of the wifi",
            },
            "returns": {
                "status": "string, ok or error",
                "message": "string, error message",
            },
        }

    def json_schema(self):
        return json.dumps(self.schema())

    def do_post(self, data: RequestData) -> tuple[int, str]:
        if "ssid" in data.data and "psk" in data.data:
            try:
                log.info("Opening WiFi connection to %s", data.data["ssid"])
                wificon = WiFiHandler(data.data["ssid"], data.data["psk"])
                data.bb.add_task(OpenWiFiConTask(data.bb.time_ms() + 500, data.bb, wificon))
                return 200, json.dumps({"status": "ok"})
            except Exception as e:
                return 500, json.dumps({"status": "error", "message": str(e)})
        else:
            return 400, json.dumps({"status": "bad request"})
