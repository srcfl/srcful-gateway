import json
from server.tasks.openDeviceTask import OpenDeviceTask
from ..handler import PostHandler
from ..requestData import RequestData
import logging
from server.inverters.IComFactory import IComFactory
from server.inverters.ICom import ICom
from server.inverters.der import DER

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
        try:
            if ICom.CONNECTION_KEY not in data.data:
                return 400, json.dumps({"status": "connection field is required"})
            
            conf = IComFactory.parse_connection_config_from_dict(data.data)
            com = IComFactory.create_com(conf)
            logger.info(f"Created a Modbus {conf[0]} connection")
            der = DER(com)
            
            data.bb.add_task(OpenDeviceTask(data.bb.time_ms() + 100, data.bb, der))
            return 200, json.dumps({"status": "ok"})    
            
        except Exception as e:
            logger.error(f"Failed to open a Modbus {conf[0]} connection: {conf}")
            logger.error(e)
            return 500, json.dumps({"status": "error", "message": str(e)})