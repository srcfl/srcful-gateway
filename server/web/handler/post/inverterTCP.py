import json
from server.inverters.InverterTCP import InverterTCP
from server.tasks.openInverterTask import OpenInverterTask

from ..handler import PostHandler
from ..requestData import RequestData

import logging

logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return self.create_schema(
            "Open an inverter and start harvesting the data",
            required={
                "ip": "string, ip address of the inverter",
                "port": "int, port of the inverter",
                "type": "string, type of inverter",
                "address": "int, address of the inverter",
            },
            returns={
                "status": "string, ok or error",
                "message": "string, error message",
            },
        )

    def do_post(self, data: RequestData) -> tuple[int, str]:
        if (
            "ip" in data.data
            and "port" in data.data
            and "type" in data.data
        ):
            try:
                conf = (
                    data.data["ip"],
                    int(data.data["port"]),
                    data.data["type"],
                    int(data.data["address"]),
                )
                inverter = InverterTCP(conf)
                logger.info("Created a TCP inverter")

                data.tasks.put(OpenInverterTask(100, data.bb, inverter))
                return 200, json.dumps({"status": "ok"})
            except Exception as e:
                logger.error("Failed to open inverter: %s", data.data)
                logger.error(e)
                return 500, json.dumps({"status": "error", "message": str(e)})
        else:
            return 400, json.dumps({"status": "bad request"})
