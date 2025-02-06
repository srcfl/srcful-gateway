import dbus
import json
import logging
from ..handler import PostHandler, GetHandler
from ..requestData import RequestData
from xml.etree import ElementTree

logger = logging.getLogger(__name__)


import dbus




def get_system_info():
    try:
        system_bus = dbus.SystemBus()
        
        # Get systemd object
        systemd = system_bus.get_object('org.freedesktop.systemd1',
                                      '/org/freedesktop/systemd1')
        
        # Get the introspection interface
        intro = dbus.Interface(systemd, 'org.freedesktop.DBus.Introspectable')
        
        # Get XML description and parse it
        xml = intro.Introspect()
        root = ElementTree.fromstring(xml)
        
        # Extract method names
        methods = []
        for interface in root.findall('interface'):
            interface_name = interface.get('name')
            interface_methods = [method.get('name') for method in interface.findall('method')]
            if interface_methods:  # Only add interfaces that have methods
                methods.append({
                    'interface': interface_name,
                    'methods': interface_methods
                })
        
        # Get system metrics that we know work
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read().strip()) / 1000
        
        with open('/proc/loadavg', 'r') as f:
            load = f.read().strip().split()[:3]
        
        with open('/proc/uptime', 'r') as f:
            uptime = float(f.read().split()[0])
        
        return {
            'available_interfaces': methods,
            'system_metrics': {
                'temperature': f"{temp}°C",
                'load_average': load,
                'uptime_seconds': uptime
            }
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'status': 'failed'
        }
    

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
