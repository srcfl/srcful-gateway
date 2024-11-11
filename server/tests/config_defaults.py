from server.devices.ICom import ICom
from server.devices.TCPDevice import TCPDevice
import server.devices.inverters as inverter
import server.devices.p1meters as p1meter
from server.network.network_utils import NetworkUtils


TCP_ARGS = {
    "connection": "TCP",
    "ip": "localhost",
    "mac": NetworkUtils.INVALID_MAC,
    "port": 502,
    "device_type": "solaredge",
    "slave_id": 4,
}

RTU_ARGS = {
    "connection": "RTU",
    "port": "/dev/ttyS0",
    "baudrate": 9600,
    "bytesize": 8,
    "parity": "N",
    "stopbits": 1,
    "device_type": "lqt40s",
    "slave_id": 1,
}

SOLARMAN_ARGS = {
    "connection": "SOLARMAN",
    "ip": "localhost",
    "mac": NetworkUtils.INVALID_MAC,
    "port": 502,
    "device_type": "deye",
    "sn": 1234567890,
    "slave_id": 1,
    "verbose": True
}

SUNSPEC_ARGS = {
    "connection": "SUNSPEC",
    "ip": "localhost",
    "mac": NetworkUtils.INVALID_MAC,
    "port": 502,
    "slave_id": 1
}

P1_TELNET_ARGS = {
    "connection": "P1Telnet",
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
RTU_CONFIG = {**RTU_ARGS, "sn": "N/A"}
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