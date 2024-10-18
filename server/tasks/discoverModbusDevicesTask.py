import logging
from .task import Task
from server.blackboard import BlackBoard
from server.network.network_utils import NetworkUtils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DiscoverModbusDevicesTask(Task):
    """
    Discover modbus devices on the network and cache the results in the blackboard.
    """
    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        
    def execute(self, event_time):
        logger.info("Discovering modbus devices")
        
        ports = NetworkUtils.DEFAULT_MODBUS_PORTS
        ports = NetworkUtils.parse_ports(ports)
        timeout = NetworkUtils.DEFAULT_TIMEOUT

        ip_port_mac_dict = NetworkUtils.get_hosts(ports=ports, timeout=timeout)
        
        self.bb.set_modbus_devices_cache(ip_port_mac_dict)

        return None
