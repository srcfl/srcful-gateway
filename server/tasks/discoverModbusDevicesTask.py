import logging
from .task import Task
from server.app.blackboard import BlackBoard
from server.network.network_utils import NetworkUtils
from server.devices.inverters.modbus_device_scanner import scan_for_modbus_devices
from server.devices.ICom import ICom
from typing import List

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DiscoverModbusDevicesTask(Task):
    """
    Discover modbus and P1 devices on the network and cache the results in the blackboard.
    """
    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        
    def execute(self, event_time):
        
        self.discover_modbus_devices()
        
        return None
    
    def discover_modbus_devices(self, ports_str: str = NetworkUtils.DEFAULT_MODBUS_PORTS, timeout: float = NetworkUtils.DEFAULT_TIMEOUT) -> List[ICom]:
        logger.info("Discovering modbus devices")
        
        ports = NetworkUtils.parse_ports(ports_str)
        
        open_devices: List[ICom] = [device for device in self.bb._devices.lst if device.is_open()]

        # Scan for modbus devices
        devices:List[ICom] = scan_for_modbus_devices(ports=ports, timeout=timeout, open_devices=open_devices)
        
        
        logger.info(f"Found {len(devices)} modbus devices")
        logger.info([device.get_config() for device in devices])
        
        self.bb.set_available_devices(devices=devices)
        
        return devices