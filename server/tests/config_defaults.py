from server.devices.ICom import ICom
from server.devices.TCPDevice import TCPDevice
import server.devices.inverters as inverter
from server.devices.inverters.ModbusSolarman import ModbusSolarman
from server.devices.inverters.ModbusSunspec import ModbusSunspec
from server.devices.inverters.ModbusTCP import ModbusTCP
import server.devices.p1meters as p1meter
from server.network.network_utils import NetworkUtils


TCP_ARGS = {
    ICom.connection_key(): "TCP",
    TCPDevice.ip_key(): "localhost",
    TCPDevice.mac_key(): NetworkUtils.INVALID_MAC,
    TCPDevice.port_key(): 502,
    ModbusTCP.device_type_key(): "solaredge",
    ModbusTCP.slave_id_key(): 4,
}

SOLARMAN_ARGS = {
    ICom.connection_key(): "SOLARMAN",
    TCPDevice.ip_key(): "localhost",
    TCPDevice.mac_key(): NetworkUtils.INVALID_MAC,
    TCPDevice.port_key(): 502,
    ModbusSolarman.device_type_key(): "deye",
    ModbusSolarman.sn_key(): 1234567890,
    ModbusSolarman.slave_id_key(): 1,
    ModbusSolarman.verbose_key(): True
}

SUNSPEC_ARGS = {
    ICom.connection_key(): "SUNSPEC",
    TCPDevice.ip_key(): "localhost",
    TCPDevice.mac_key(): NetworkUtils.INVALID_MAC,
    TCPDevice.port_key(): 502,
    ModbusSunspec.slave_id_key(): 1
}

P1_TELNET_ARGS = {
    ICom.connection_key(): "P1Telnet",
    "ip": "localhost",
    "port": 23,
}

ENPHASE_ARGS = {
    ICom.connection_key(): "ENPHASE", 
    TCPDevice.ip_key(): "192.168.1.110",
    inverter.Enphase.bearer_token_key(): "eyJraWQiOiIasdasdadsI1NiJ9.eyJhdWQiOiIyMDIyMTUwMDMwMjgiLCJpc3Miasdn21wmVEUuQ"
}

P1_JEMAC_ARGS = {
    ICom.connection_key(): "P1Jemac",
    TCPDevice.ip_key(): "192.168.1.110",
}

# Config snapshots after device creation
TCP_CONFIG = {**TCP_ARGS, "sn": NetworkUtils.INVALID_MAC}
SOLARMAN_CONFIG = {**SOLARMAN_ARGS, "sn": 1234567890}
SUNSPEC_CONFIG = {**SUNSPEC_ARGS, "sn": "SUNSPEC135792468"}
P1_TELNET_CONFIG = {**P1_TELNET_ARGS, "meter_serial_number": "abc5qwerty"}
ENPHASE_CONFIG = {**ENPHASE_ARGS, "sn": "00:00:00:00:00:00"}

class_config_map = {
    inverter.ModbusTCP: TCP_ARGS,
    inverter.ModbusSolarman: SOLARMAN_ARGS,
    inverter.ModbusSunspec: SUNSPEC_ARGS,
    inverter.Enphase: ENPHASE_ARGS,
    p1meter.P1Telnet: P1_TELNET_ARGS,
    p1meter.P1Jemac: P1_JEMAC_ARGS,
}