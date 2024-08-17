import json
from server.inverters.SolarmanTCP import ModbusSolarman
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
                "serial": "int, serial of the data logger",
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
            and "serial" in data.data
            and "port" in data.data
            and "type" in data.data
            and "address" in data.data
        ):
            try:
                conf = (
                    data.data["ip"],
                    int(data.data["serial"]),
                    int(data.data["port"]),
                    data.data["type"],
                    int(data.data["address"]),
                    0
                )
                inverter = ModbusSolarman(conf) 
                logger.info("Created a SolarmanV5 inverter")

                data.bb.add_task(OpenInverterTask(data.bb.time_ms() + 100, data.bb, inverter))
                return 200, json.dumps({"status": "ok"})
            except Exception as e:
                logger.error("Failed to open inverter: %s", data.data)
                logger.error(e)
                return 500, json.dumps({"status": "error", "message": str(e)})
        else:
            return 400, json.dumps({"status": "bad request"})
