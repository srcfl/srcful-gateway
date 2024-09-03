import json
from server.inverters.ModbusRTU import ModbusRTU
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
                "port": "string, Serial port used for communication",
                "baudrate": "int, Bits per second",
                "bytesize": "int, Number of bits per byte 7-8",
                "parity": "string, 'E'ven, 'O'dd or 'N'one",
                "stopbits": "float, Number of stop bits 1, 1.5, 2",
                "type": "string, solaredge, huawei or fronius etc...",
                "address": "int, Modbus address of the inverter",
            },
            "returns": {
                "status": "string, ok or error",
                "message": "string, error message",
            },
        }

    def json_schema(self):
        return json.dumps(self.schema())

    def do_post(self, data: RequestData) -> tuple[int, str]:
        if "port" in data.data and "type" in data.data:
            try:
                conf = (
                    data.data["port"],
                    int(data.data["baudrate"]),
                    int(data.data["bytesize"]),
                    data.data["parity"],
                    float(data.data["stopbits"]),
                    data.data["type"],
                    int(data.data["address"]),
                )
                inverter = ModbusRTU(conf)
                logger.info("Created an RTU inverter")

                data.bb.add_task(OpenInverterTask(data.bb.time_ms() + 100, data.bb, inverter))
                return 200, json.dumps({"status": "ok"})
            except Exception as e:
                logger.error("Failed to open inverter: %s", data.data)
                logger.error(e)
                return 500, json.dumps({"status": "error", "message": str(e)})
        else:
            return 400, json.dumps({"status": "bad request"})