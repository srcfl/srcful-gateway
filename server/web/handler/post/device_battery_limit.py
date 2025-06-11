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
            "description": "Set battery power limit in Watts for a specific device",
            "returns": {"status": "success|error", "message": "string"},
        }

    def do_post(self, data: RequestData):

        if "limit" not in data.post_params:
            return 400, json.dumps({"status": "error", "message": "Limit not found"})

        # Check that limit is a positive integer
        try:
            limit: int = int(data.post_params["limit"])
            if limit <= 0:
                return 400, json.dumps({"status": "error", "message": "Battery power limit must be positive"})
        except ValueError:
            return 400, json.dumps({"status": "error", "message": "Limit is not a valid integer: " + data.post_params["limit"]})

        device_sn = data.post_params.get("device_sn", "none")

        for device in data.bb.devices.lst:
            if device.sn == device_sn:
                dee_decoder: SungrowDeeDecoder = device.get_dee_decoder()
                if dee_decoder:
                    dee_decoder.set_battery_power_limit(limit)
                    logger.info(f"Set battery power limit to {limit}W for device {device_sn}")
                    return 200, json.dumps({"status": "success", "message": f"Battery power limit set to {limit}W for device {device_sn}"})
                else:
                    return 400, json.dumps({"status": "error", "message": "Device does not have a DEE decoder"})

        return 404, json.dumps({"status": "error", "message": f"Device with serial number {device_sn} not found"})
