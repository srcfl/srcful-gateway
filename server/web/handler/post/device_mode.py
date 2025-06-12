import json
import logging

from ..handler import PostHandler
from ..requestData import RequestData
from server.devices.Device import DeviceMode


logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "Sets the device mode",
            "returns": {"status": "success|error, message:string"},
        }

    def do_post(self, data: RequestData):

        mode: DeviceMode = DeviceMode.NONE
        if data.post_params.get("mode", "none") == "read":
            mode = DeviceMode.READ
        elif data.post_params.get("mode", "none") == "self_consumption":
            mode = DeviceMode.SELF_CONSUMPTION
        elif data.post_params.get("mode", "none") == "control":
            mode = DeviceMode.CONTROL

        if mode == DeviceMode.NONE:
            return 400, json.dumps({"status": "error", "message": "Invalid mode"})

        for device in data.bb.devices.lst:
            if device.sn == data.post_params.get("device_sn", "none"):
                device.set_mode(mode)
                if device.get_mode() == mode:
                    return 200, json.dumps({"status": "success", "message": "Device mode set to " + data.post_params.get("mode", "none")})
                else:
                    return 500, json.dumps({"status": "error", "message": "Failed to set device mode, device is not controllable"})

        return 404, json.dumps({"status": "error", "message": "Device not found"})

        return 200, json.dumps([data.post_params.get("device_sn", "none"), data.post_params.get("mode", "none")])
