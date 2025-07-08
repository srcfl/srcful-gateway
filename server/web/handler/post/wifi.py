import json
import logging
from server.network.network_utils import NetworkUtils
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
            "optional": {
                "timeout": "int, timeout in seconds to wait for the connection to be established",
            },
            "returns": {
                "status": "string, ok or error",
                "message": "string, error message",
            },
        }

    def json_schema(self):
        return json.dumps(self.schema())

    def do_post(self, data: RequestData) -> tuple[int, str]:
        try:
            ssid: str = data.data.get("ssid")
            psk: str = data.data.get("psk")
            timeout: int = data.data.get("timeout", 10)

            if not ssid or not psk:
                return 422, json.dumps({"status": "error",
                                        "message": "ssid and psk are required"})

            log.info(f"Connecting to WiFi {ssid} with timeout {timeout}")

            if NetworkUtils.connect_to_wifi(ssid, psk, timeout):
                return 200, json.dumps({"status": "Successfully connected to WiFi"})
            # Upstream/temporary failure
            return 503, json.dumps({"status": "error",
                                    "message": "Failed to connect to WiFi"})
        except Exception:
            log.exception("Unexpected error while configuring WiFi")
            return 500, json.dumps({"status": "error",
                                    "message": "Internal server error"})
