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

def create_rest_device_msn(meter_serial_number:Optional[str], host: HostInfo) -> Optional[ICom]:
    from server.devices.p1meters.P1Jemac import P1Jemac
    from server.devices.p1meters.P1HomeWizard import P1HomeWizard

    constructors = {
        "Jemac": P1Jemac,
        "HomeWizard": P1HomeWizard
    }

    for key, constructor in constructors.items():

        if meter_serial_number:
            p1 = constructor(host.ip, host.port, meter_serial_number)
        else:
            p1 = constructor(host.ip, host.port)
        meter = _connect_device(p1, f"Could not create P1 {key} from {host.ip}:{host.port} with serial number {meter_serial_number}")
        if meter:
            return meter
        
    return None

def create_telnet_device_msn(meter_serial_number:Optional[str], host: HostInfo) -> Optional[ICom]:
    from server.devices.p1meters.P1Telnet import P1Telnet
    if meter_serial_number:
        p1 = P1Telnet(host.ip, host.port, meter_serial_number)
    else:
        p1 = P1Telnet(host.ip, host.port)
    return _connect_device(p1, f"Could not create P1 Telnet from {host.ip}:{host.port} with serial number {meter_serial_number}")