import dbus
import json
import logging
from ..handler import PostHandler
from ..requestData import RequestData

logger = logging.getLogger(__name__)

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
