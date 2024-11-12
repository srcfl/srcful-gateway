from typing import Optional
from server.devices.ICom import ICom
from server.network.network_utils import HostInfo
import logging

logger = logging.getLogger(__name__)


def _connect_device(p1: ICom, error_message: str) -> Optional[ICom]:
    try:
        if p1.connect():
            return p1
    except Exception as e:
        logger.info(f"{error_message}: {str(e)}")
    return None

def create_rest_device(meter_serial_number:str, host: HostInfo) -> Optional[ICom]:
    from server.devices.p1meters.P1Jemac import P1Jemac

    p1 = P1Jemac(host.ip, host.port, meter_serial_number)
    return _connect_device(p1, f"Could not create P1 Jemac from {host.ip}:{host.port}")

def create_telnet_device(meter_serial_number:str, host: HostInfo) -> Optional[ICom]:
    from server.devices.p1meters.P1Telnet import P1Telnet

    p1 = P1Telnet(host.ip, host.port, meter_serial_number)
    return _connect_device(p1, f"Could not create P1 Telnet from {host.ip}:{host.port}")