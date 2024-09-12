import json
from server.tasks.openDeviceTask import OpenDeviceTask
from ..handler import PostHandler
from ..requestData import RequestData
import logging
from server.inverters.IComFactory import IComFactory
from server.inverters.ICom import ICom
from server.inverters.der import DER

logger = logging.getLogger(__name__)


class Handler(PostHandler):
    def schema(self):
        return self.create_schema(
            "Open an inverter and start harvesting the data",
            required={
                "connection": "string, type of modbus connection (e.g., 'TCP', 'RTU', 'SOLARMAN', 'SUNSPEC')",
            },
            optional={
                "ip": "string, IP address of the inverter (for TCP, SOLARMAN, SUNSPEC)",
                "port": "int, port of the inverter (for TCP, SOLARMAN, SUNSPEC)",
                "serial_port": "string, serial port of the inverter (for RTU)",
                "serial": "string, serial number (for SOLARMAN)",
                "baudrate": "int, baudrate for serial connection (for RTU)",
                "bytesize": "int, bytesize for serial connection (for RTU)",
                "parity": "string, parity for serial connection (for RTU)",
                "stopbits": "int, stop bits for serial connection (for RTU)",
                "inverter_type": "string, specific inverter model or type",
                "slave_id": "int, Modbus slave ID or address of the inverter",
            },
            returns={
                "status": "string, ok or error",
                "message": "string, error message",
            },
        )
    def do_post(self, data: RequestData) -> tuple[int, str]:
        
        try:
            if ICom.CONNECTION_KEY not in data.data:
                return 400, json.dumps({"status": "connection field is required"})
            
            conf = IComFactory.parse_connection_config_from_dict(data.data)
            com = IComFactory.create_com(conf)
            logger.info(f"Created a Modbus {conf[0]} connection")
            
            data.bb.add_task(OpenDeviceTask(data.bb.time_ms() + 100, data.bb, com))
            return 200, json.dumps({"status": "ok"})    
            
        except Exception as e:
            logger.error(f"Failed to open a Modbus {conf[0]} connection: {conf}")
            logger.error(e)
            return 500, json.dumps({"status": "error", "message": str(e)})