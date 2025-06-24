import json
from ..handler import GetHandler
from ..requestData import RequestData
from server.web.handler.get.modbus import ModbusParameter


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns a simple hello world message",
            "returns": {"message": "hello world from srcful!"},
        }

    def do_get(self, request_data: RequestData):
        device_id: str = request_data.query_params.get(ModbusParameter.DEVICE_ID, None)

        if device_id is None:
            return 400, json.dumps({"error": "missing device index"})

        device = request_data.bb.devices.find_sn(device_id)
        if device is None:
            return 400, json.dumps({"error": f"device {device_id} not found"})

        ret = device.get_esystem_data()

        return 200, json.dumps(ret)
