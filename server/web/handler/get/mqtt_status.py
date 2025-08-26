import json
from ..handler import GetHandler
from ..requestData import RequestData


class Handler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Returns the status of the MQTT service",
            "returns": "MQTT service status as a json object",
        }

    def do_get(self, data: RequestData):
        if not data.bb.mqtt_service:
            return 503, json.dumps({
                "error": "MQTT service not initialized",
                "connected": False
            })
        
        stats = data.bb.mqtt_service.get_stats()
        return 200, json.dumps(stats)
