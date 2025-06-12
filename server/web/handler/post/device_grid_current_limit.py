import json
import logging

from ..handler import PostHandler
from ..requestData import RequestData
from server.devices.DeeDecoder import SungrowDeeDecoder

logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "Set grid current limit in Amperes for a specific device",
            "returns": {"status": "success|error", "message": "string"},
        }

    def do_post(self, data: RequestData):

        if "current" not in data.post_params:
            return 400, json.dumps({"status": "error", "message": "Current limit not found"})

        # Check that current limit is a positive integer
        try:
            limit: int = int(data.post_params["current"])
            if limit <= 0:
                return 400, json.dumps({"status": "error", "message": "Grid current limit must be positive"})
        except ValueError:
            return 400, json.dumps({"status": "error", "message": "Current limit is not a valid integer: " + data.post_params["current"]})

        device_sn = data.post_params.get("device_sn", "none")

        for device in data.bb.devices.lst:
            if device.sn == device_sn:
                dee_decoder: SungrowDeeDecoder = device.get_dee_decoder()
                if dee_decoder:
                    dee_decoder.set_grid_current_limit(limit)
                    logger.info(f"Set grid current limit to {limit}A for device {device_sn}")
                    return 200, json.dumps({"status": "success", "message": f"Grid current limit set to {limit}A for device {device_sn}"})
                else:
                    return 400, json.dumps({"status": "error", "message": "Device does not have a DEE decoder"})

        return 404, json.dumps({"status": "error", "message": f"Device with serial number {device_sn} not found"})
