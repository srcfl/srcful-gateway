from typing import Optional
from server.devices.ICom import ICom
from server.network.network_utils import HostInfo

def create_enphase_device_msn(mac:Optional[str], host: HostInfo) -> Optional[ICom]:
    from server.devices.inverters.enphase import Enphase
    return Enphase(mac, host.ip, host.port)
