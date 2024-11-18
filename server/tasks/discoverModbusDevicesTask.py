import logging

from server.devices.inverters.ModbusTCP import ModbusTCP
from .task import Task
from server.app.blackboard import BlackBoard
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

        hosts = NetworkUtils.get_hosts(ports=ports, timeout=timeout)
        
        icoms = []
        for host in hosts:
            args = {
                ModbusTCP.ip_key(): host.ip,
                ModbusTCP.port_key(): host.port,
                ModbusTCP.mac_key(): host.mac
            }
            
            icoms.append(ModbusTCP(**args))
        
        self.bb.set_available_devices(icoms)

        return None
