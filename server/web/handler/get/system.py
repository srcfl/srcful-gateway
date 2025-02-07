import json
import logging
import dbus

from server.app.blackboard import BlackBoard
from server.app.isystem_time import ISystemTime
from ..handler import GetHandler
from ..requestData import RequestData

logger = logging.getLogger(__name__)

class SystemHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Get basic system metrics",
            "returns": {
                "temperature": "float, CPU temperature in Celsius",
                "processes_average": "dict, load averages for 1, 5 and 15 minutes",
                "uptime_seconds": "float, system uptime in seconds"
            }
        }

    def _get_basic_metrics(self, t: ISystemTime):
        try:
            # Get system metrics
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000
            
            with open('/proc/loadavg', 'r') as f:
                load_values = f.read().strip().split()[:3]
                load_avg = {
                    'last_1min': float(load_values[0]),
                    'last_5min': float(load_values[1]),
                    'last_15min': float(load_values[2]),
                }
            
            with open('/proc/uptime', 'r') as f:
                uptime = float(f.read().split()[0])

            with open('/proc/meminfo', 'r') as f:
                mem_info = {}
                for line in f:
                    if 'MemTotal' in line or 'MemAvailable' in line or 'MemFree' in line:
                        key, value = line.split(':')
                        # Convert kB to MB and remove 'kB' string
                        value_mb = int(value.strip().split()[0]) / 1024
                        mem_info[key.strip()] = round(value_mb, 2)
            
            return {
                'time_utc_sec': int(t.time_ms() / 1000),
                'temperature_celsius': temp,
                'processes_average': load_avg,
                'uptime_seconds': uptime,
                'memory_MB': {
                    'total': mem_info['MemTotal'],
                    'available': mem_info['MemAvailable'],
                    'free': mem_info['MemFree'],
                    'used': round(mem_info['MemTotal'] - mem_info['MemAvailable'], 2),
                    'percent_used': round((1 - (mem_info['MemAvailable'] / mem_info['MemTotal'])) * 100, 1)
                }
            }
        except Exception as e:
            logger.error(f"Failed to get basic metrics: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }

    def do_get(self, data: RequestData) -> tuple[int, str]:
        metrics = self._get_basic_metrics(data.bb)
        return 200, json.dumps(metrics)


class SystemDetailsHandler(GetHandler):
    def schema(self):
        return {
            "type": "get",
            "description": "Get detailed system information via DBus",
            "returns": {
                "systemd_properties": "dict, systemd manager properties"
            }
        }

    def _get_dbus_details(self):
        try:
            system_bus = dbus.SystemBus()
            systemd = system_bus.get_object('org.freedesktop.systemd1',
                                          '/org/freedesktop/systemd1')
            
            # Get properties interface
            props = dbus.Interface(systemd, 'org.freedesktop.DBus.Properties')
            manager_props = props.GetAll('org.freedesktop.systemd1.Manager')
            
            # Convert DBus values to strings
            clean_props = {str(k): str(v) for k, v in manager_props.items()}
            
            return {
                'systemd_properties': clean_props
            }
        except Exception as e:
            logger.error(f"Failed to get DBus details: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }

    def do_get(self, data: RequestData) -> tuple[int, str]:
        details = self._get_dbus_details()
        return 200, json.dumps(details) 