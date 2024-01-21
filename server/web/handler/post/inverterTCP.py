import json
from server.inverters.InverterTCP import InverterTCP
from server.tasks.openInverterTask import OpenInverterTask

from ..handler import PostHandler
from ..requestData import RequestData

import logging

logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "open an inverter",
            "required": {
                "ip": "string, ip address of the inverter",
                "port": "int, port of the inverter",
                "type": "string, type of inverter",
                "address": "int, address of the inverter",
            },
            "returns": {
                "status": "string, ok or error",
                "message": "string, error message",
            },
        }

    def json_schema(self):
        return json.dumps(self.schema())

    def do_post(self, request_data: RequestData) -> tuple[int, str]:
        if (
            "ip" in request_data.data
            and "port" in request_data.data
            and "type" in request_data.data
        ):
            try:
                conf = (
                    request_data.data["ip"],
                    int(request_data.data["port"]),
                    request_data.data["type"],
                    int(request_data.data["address"]),
                )
                inverter = InverterTCP(conf)
                logger.info("Created a TCP inverter")

                request_data.tasks.put(OpenInverterTask(100, request_data.bb, inverter))
                return 200, json.dumps({"status": "ok"})
            except Exception as e:
                logger.error("Failed to open inverter: {}".format(request_data.data))
                logger.error(e)
                return 500, json.dumps({"status": "error", "message": str(e)})
        else:
            return 400, json.dumps({"status": "bad request"})
