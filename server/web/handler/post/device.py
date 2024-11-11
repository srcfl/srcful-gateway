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

        connection_schema = []
        for connection_type, config in connection_configs.items():
            connection_schema.append(config)

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
            if ICom.connection_key() not in data.data:
                logger.error(f"Missing or invalid connection type")
                return 400, json.dumps({"status": "error", "message": "Missing or invalid connection type"})
        
            com = IComFactory.create_com(data.data)
            
            # config = {ICom.CONNECTION_KEY: connection_type, **data.data[connection_type]}
            # com = IComFactory.create_com(config)
            logger.info(f"Created a device {com.get_config()} connection")
            
            data.bb.add_task(OpenDeviceTask(data.bb.time_ms() + 100, data.bb, com))
            return 200, json.dumps({"status": "ok"})
            
        except Exception as e:
            logger.error(f"Failed to open a device connection: {str(e)}")
            return 500, json.dumps({"status": "error", "message": str(e)})