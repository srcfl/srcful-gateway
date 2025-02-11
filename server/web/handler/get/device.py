import json

from server.devices.IComFactory import IComFactory
from ..handler import GetHandler

from ..requestData import RequestData


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns the configuration of the running devices, details depend on the device type.",
            "returns": [{
                "connection": "string, connection type (TCP, RTU, SOLARMAN, P1TELNET)",
                "status": "string, open, closed or No inverter",
                "id": "unique id of the device",
                "config": "dict, device specific configuration",
            
            }],
        }
    
    def _fix_config(self, config: dict, id: str, status: str):
        config["id"] = id
        config["status"] = status
        return config

    def do_get(self, data: RequestData):
        configs = data.bb.devices_state_to_dict(data.bb.devices.lst)
        raw_configs = [device.get_config() for device in data.bb.devices.lst]

        # aklso add devices that happen to be in settings only, this can happen if the gw is rebooted and the device in settings cannot be found anymore
        for config in data.bb.settings.devices.connections:
            if config not in raw_configs:
                device = IComFactory.create_com(config)
                configs.append(data.bb.get_device_state(device))

        return 200, json.dumps(configs)
