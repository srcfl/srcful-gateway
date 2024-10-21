import json
from server.tasks.openDeviceTask import OpenDeviceTask
from ..handler import PostHandler
from ..requestData import RequestData
import logging
from server.devices.IComFactory import IComFactory
from server.devices.ICom import ICom

logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        connection_configs = IComFactory.get_connection_configs()

        connection_schema = {}
        for connection_type, config in connection_configs.items():
            connection_schema[connection_type] = {
                "type": "object",
                "properties": config,
                "required": list(config.keys())
            }

        return self.create_schema(
            "Open a device and start harvesting data. Use one of the required objects.",
            required=connection_schema,
            optional={},
            returns={
                "status": "string, ok or error",
                "message": "string, error message",
            },
        )

    def do_post(self, data: RequestData) -> tuple[int, str]:
        logger.info(f"Device enpoint Received data: {data.data}")
        try:
            connection_types = IComFactory.get_supported_connections()
            connection_type = next((ct for ct in connection_types if ct in data.data), None)
            logger.info(f"Connection type: {connection_type}")
            if not connection_type:
                logger.error(f"Missing or invalid connection type")
                return 400, json.dumps({"status": "error", "message": "Missing or invalid connection type"})
            
            config = {ICom.CONNECTION_KEY: connection_type, **data.data[connection_type]}
            com = IComFactory.create_com(config)
            logger.info(f"Created a device {connection_type} connection")
            
            data.bb.add_task(OpenDeviceTask(data.bb.time_ms() + 100, data.bb, com))
            return 200, json.dumps({"status": "ok"})   
            
        except Exception as e:
            logger.error(f"Failed to open a device connection: {str(e)}")
            return 500, json.dumps({"status": "error", "message": str(e)})