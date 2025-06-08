import logging
from .task import Task
from server.app.blackboard import BlackBoard
from server.network.network_utils import NetworkUtils
from server.tasks.discover_mdns_devices_task import DiscoverMdnsDevicesTask
from server.tasks.discoverModbusDevicesTask import DiscoverModbusDevicesTask
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

        self.discover_devices()

        return None

    def discover_devices(self, ports_str: str = NetworkUtils.DEFAULT_MODBUS_PORTS, timeout: float = NetworkUtils.DEFAULT_TIMEOUT) -> List[ICom]:
        logger.info("Discovering modbus devices")

        devices: List[ICom] = []

        # Discover mdns devices
        mdns_devices: List[ICom] = DiscoverMdnsDevicesTask(event_time=0, bb=self.bb).discover_mdns_devices()
        devices.extend(mdns_devices)
        self.bb.set_available_devices(devices=devices)

        # Discover modbus devices
        modbus_devices: List[ICom] = DiscoverModbusDevicesTask(event_time=0, bb=self.bb).discover_modbus_devices(ports_str=ports_str, timeout=timeout)
        devices.extend(modbus_devices)
        self.bb.set_available_devices(devices=devices)

        # Discover P1 devices
        p1_devices: List[ICom] = scan_for_p1_devices()
        devices.extend(p1_devices)
        self.bb.set_available_devices(devices=devices)

        logger.info(f"Devices: Found {len(devices)} devices")
        logger.info([device.get_config() for device in devices])

        return devices
