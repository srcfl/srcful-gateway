import logging

from server.devices.inverters.ModbusTCP import ModbusTCP
from .task import Task
from server.app.blackboard import BlackBoard
from server.network.network_utils import NetworkUtils
from server.devices.inverters.modbus_device_scanner import scan_for_modbus_devices
from server.devices.p1meters.p1_scanner import scan_for_p1_devices
from server.devices.ICom import ICom
from typing import List 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DiscoverDevicesTask(Task):
    """
    Discover modbus and P1 devices on the network and cache the results in the blackboard.
    """
    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        
    def execute(self, event_time):
        logger.info("Discovering modbus devices")
        
        ports = NetworkUtils.DEFAULT_MODBUS_PORTS
        ports = NetworkUtils.parse_ports(ports)
        timeout = NetworkUtils.DEFAULT_TIMEOUT

        # Scan for modbus devices
        devices:List[ICom] = scan_for_modbus_devices(ports=ports, timeout=timeout)
        
        # Scan for P1 devices
        p1_devices:List[ICom] = scan_for_p1_devices()
        
        # append p1 devices to the devices list
        devices.extend(p1_devices)
        
        logger.info(f"Found {len(devices)} devices")
        logger.info([device.get_config() for device in devices])
        
        self.bb.set_available_devices(devices=devices)

        return None
