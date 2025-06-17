import json
import logging

from ..handler import GetHandler
from ..requestData import RequestData

log = logging.getLogger(__name__)


class Handler(GetHandler):
    def schema(self) -> dict:
        return self.create_schema(
            "Get all stored device connections",
            returns={
                "connections": [
                    {
                        "ip": "string, device IP address",
                        "sn": "string, device serial number",
                        "mac": "string, device MAC address",
                        "port": "integer, device port",
                        "slave_id": "integer, modbus slave ID",
                        "connection": "string, connection type (TCP, RTU, etc.)",
                        "device_type": "string, device type (sungrow, huawei, etc.)"
                    }
                ]
            }
        )

    def do_get(self, data: RequestData):
        try:
            connections = data.bb.storage.get_connections()
            return 200, json.dumps({"connections": connections})
        except Exception as e:
            log.error(f"Error retrieving connections: {str(e)}")
            return 500, json.dumps({"error": f"Failed to retrieve connections: {str(e)}"})
