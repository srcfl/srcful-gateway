import json
from server.inverters.InverterRTU import InverterRTU
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

    def do_post(self, request_data: RequestData) -> tuple[int, str]:
        if "port" in request_data.data and "type" in request_data.data:
            try:
                conf = (
                    request_data.data["port"],
                    int(request_data.data["baudrate"]),
                    int(request_data.data["bytesize"]),
                    request_data.data["parity"],
                    float(request_data.data["stopbits"]),
                    request_data.data["type"],
                    int(request_data.data["address"]),
                )
                inverter = InverterRTU(conf)
                logger.info("Created an RTU inverter")

                request_data.tasks.put(OpenInverterTask(100, request_data.bb, inverter))
                return 200, json.dumps({"status": "ok"})
            except Exception as e:
                logger.error("Failed to open inverter: {}".format(request_data.data))
                logger.error(e)
                return 500, json.dumps({"status": "error", "message": str(e)})
        else:
            return 400, json.dumps({"status": "bad request"})
