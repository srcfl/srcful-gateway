import dbus
import json
import logging
from ..handler import PostHandler, GetHandler
from ..requestData import RequestData

logger = logging.getLogger(__name__)


def get_system_info() -> dict:
    try:
        system_bus = dbus.SystemBus()
        
        # Get systemd info
        systemd = system_bus.get_object('org.freedesktop.systemd1',
                                      '/org/freedesktop/systemd1')
        manager = dbus.Interface(systemd, 'org.freedesktop.systemd1.Manager')
        
        # Get system state
        state = manager.Get('org.freedesktop.systemd1.Manager', 'SystemState')
        
        # Get system uptime
        uptime = manager.Get('org.freedesktop.systemd1.Manager', 'UserspaceTimestamp')
        
        # Get temperature (requires thermal_zone0)
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read().strip()) / 1000  # Convert millicelsius to celsius
        
        # Get system load
        with open('/proc/loadavg', 'r') as f:
            load = f.read().strip().split()[:3]
        
        return {
            'system_state': str(state),
            'uptime': str(uptime),
            'temperature': f"{temp}°C",
            'load_average': load
        }
        
    except Exception as e:
        print(f"Error getting system info: {e}")
        return {}


class SystemHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Get the system status",
            "returns": {
                "success": "boolean indicating if system status was retrieved",
                "message": "string with status message"
            }
        }

    def do_get(self, data: RequestData) -> tuple[int, str]:
        return 200, json.dumps(get_system_info())
    

class Handler(PostHandler):
    def schema(self):
        return {
            "type": "post",
            "description": "Reboot the system",
            "returns": {
                "success": "boolean indicating if reboot was initiated",
                "message": "string with status message"
            }
        }

    def do_post(self, data: RequestData) -> tuple[int, str]:
        try:
            # Connect to system bus
            system_bus = dbus.SystemBus()
            
            # Get systemd manager object
            systemd = system_bus.get_object('org.freedesktop.systemd1',
                                          '/org/freedesktop/systemd1')
            
            # Get manager interface
            manager = dbus.Interface(systemd, 'org.freedesktop.systemd1.Manager')
            
            # Reboot
            manager.Reboot()
            
            return 200, json.dumps({
                "success": True,
                "message": "System reboot initiated"
            })
            
        except Exception as e:
            error_msg = f"Failed to reboot system: {str(e)}"
            logger.error(error_msg)
            return 500, json.dumps({
                "success": False,
                "error": error_msg
            })
