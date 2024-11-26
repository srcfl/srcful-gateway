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
        configs = []

        raw_configs = []

        for device in data.bb.devices.lst:
            config = device.get_config()
            raw_configs.append(config)

            device_config = self._fix_config(config, device.get_SN(), "open" if device.is_open() else "closed")

            configs.append(device_config)

        for config in data.bb.settings.devices.connections:
            if config not in raw_configs:
                device = IComFactory.create_com(config)
                config = self._fix_config(device.get_config(), device.get_SN(), "pending")
                configs.append(config)

        return 200, json.dumps(configs)
