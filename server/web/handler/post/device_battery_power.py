import json
import logging

from ..handler import PostHandler
from ..requestData import RequestData
from server.devices.Device import DeviceCommand, DeviceCommandType, DeviceMode


logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "set battery power in W negative for discharge, positive for charge",
            "returns": {"status": "success|error, message:string"},
        }

    def do_post(self, data: RequestData):

        if "power" not in data.post_params:
            return 400, json.dumps({"status": "error", "message": "Power not found"})

        logger.info(f"Setting battery power to {data.post_params['power']} for device {data.post_params.get('device_sn', 'none')}")

        # check that power is an integer
        try:
            power: int = int(data.post_params["power"])
        except ValueError:
            return 400, json.dumps({"status": "error", "message": "Power is not an integer: " + data.post_params["power"]})

        command = DeviceCommand(DeviceCommandType.SET_BATTERY_POWER, power)

        for device in data.bb.devices.lst:
            if device.sn == data.post_params.get("device_sn", "none"):
                if device.get_mode() == DeviceMode.CONTROL:
                    device.add_command(command)
                    logger.info(f"Device {device.sn} added command to set battery power to {power}")
                    return 200, json.dumps({"status": "success", "message": "Device battery power set to " + str(power)})
                else:
                    logger.info(f"Device {device.sn} is not in control mode")
                    return 400, json.dumps({"status": "error", "message": "Device is not in control mode"})

        return 404, json.dumps({"status": "error", "message": "Device not found"})
