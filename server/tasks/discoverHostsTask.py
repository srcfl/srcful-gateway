from server.network.network_utils import NetworkUtils
from server.tasks.task import Task
from server.app.blackboard import BlackBoard
from server.network.network_utils import HostInfo
from typing import List
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DiscoverHostsTask(Task):
    """
    Discover hosts on the network and cache the results in the blackboard.
    """

    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)

    def execute(self, event_time):
        ports = NetworkUtils.parse_ports(NetworkUtils.DEFAULT_MODBUS_PORTS)
        hosts: List[HostInfo] = NetworkUtils.get_hosts(ports=ports, timeout=NetworkUtils.DEFAULT_TIMEOUT)

        logger.info(f"Hosts: Found {len(hosts)} hosts")

        self.bb.set_available_hosts(hosts)
        return None
