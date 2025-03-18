from server.network.mdns.mdns import scan_for_compatible_devices, ServiceResult
from server.devices.ICom import ICom
from server.devices.inverters.enphase import Enphase
from server.tasks.task import Task
from server.app.blackboard import BlackBoard
from typing import List
import logging
from server.network.network_utils import NetworkUtils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DiscoverMdnsDevicesTask(Task):
    """
    Discover hosts on the network and cache the results in the blackboard.
    """

    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)

    def execute(self, event_time):
        self.discover_mdns_devices()

    def discover_mdns_devices(self) -> List[ICom]:

        devices: List[ICom] = []
        service_results: List[ServiceResult] = scan_for_compatible_devices()

        logger.info(f"MDNS: Found {len(service_results)} devices")

        for service_result in service_results:
            logger.info(f"Found device: {service_result.name}, {service_result.address}, {service_result.port}, {service_result.properties}")

            if service_result.name == "envoy._enphase-envoy._tcp.local.":
                iq_gw_serial = service_result.properties.get("serialnum", "")
                devices.append(Enphase(iq_gw_serial=iq_gw_serial,
                                       ip=service_result.address,
                                       port=service_result.port,
                                       mac=NetworkUtils.get_mac_from_ip(service_result.address)))

        return devices
