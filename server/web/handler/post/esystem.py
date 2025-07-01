import json
from server.e_system.e_system import ESystemTemplate
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
            "Sets the devices used in the energy system",
            required={"battery": "list of objects, like {\"sn\": \"string device sn\"}",
                      "solar": "list of objects, like {\"sn\": \"string device sn\"}",
                      "load": "list of objects, like {\"sn\": \"string device sn\"}",
                      "grid": "list of objects, like {\"sn\": \"string device sn\"}"},
            optional={},
            returns={
                "status": "string, ok or error",
                "message": "string, error message",
            },
        )

    def do_post(self, data: RequestData) -> tuple[int, str]:
        logger.info(f"Device enpoint Received data: {data.data}")

        
        try:            
            esystem = ESystemTemplate()

            for battery_sn in data.data["battery"]:
                battery = data.bb.devices.find_sn(battery_sn)
                if battery is None:
                    logger.error(f"Battery {battery_sn} not found")
                    return 400, json.dumps({"status": "error", "message": f"Battery {battery_sn} not found"})
                if not esystem.add_battery_sn(battery):
                    logger.error(f"Device {battery_sn} does not represent a battery")
                    return 400, json.dumps({"status": "error", "message": f"Device {battery_sn} does not represent a battery"})
                
            for solar_sn in data.data["solar"]:
                solar = data.bb.devices.find_sn(solar_sn)
                if solar is None:
                    logger.error(f"Solar {solar_sn} not found")
                    return 400, json.dumps({"status": "error", "message": f"Solar {solar_sn} not found"})
                if not esystem.add_solar_sn(solar):
                    logger.error(f"Device {solar_sn} does not represent a solar panel")
                    return 400, json.dumps({"status": "error", "message": f"Device {solar_sn} does not represent a solar panel"})
                
            for load_sn in data.data["load"]:
                load = data.bb.devices.find_sn(load_sn)
                if load is None:
                    logger.error(f"Load {load_sn} not found")
                    return 400, json.dumps({"status": "error", "message": f"Load {load_sn} not found"})
                if not esystem.add_load_sn(load):
                    logger.error(f"Device {load_sn} does not represent a load")
                    return 400, json.dumps({"status": "error", "message": f"Device {load_sn} does not represent a load"})
                
            for grid_sn in data.data["grid"]:
                grid = data.bb.devices.find_sn(grid_sn)
                if grid is None:
                    logger.error(f"Grid {grid_sn} not found")
                    return 400, json.dumps({"status": "error", "message": f"Grid {grid_sn} not found"})
                if not esystem.add_grid_sn(grid):
                    logger.error(f"Device {grid_sn} does not represent a grid meter")
                    return 400, json.dumps({"status": "error", "message": f"Device {grid_sn} does not represent a grid meter"})
                
            data.bb.esystem = esystem
            return 200, json.dumps({"status": "ok"})
            
        except Exception as e:
            logger.error(f"Failed to open a device connection: {str(e)}")
            return 500, json.dumps({"status": "error", "message": str(e)})