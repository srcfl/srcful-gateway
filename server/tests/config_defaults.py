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

# Config snapshots after device creation
TCP_CONFIG = {**TCP_ARGS, "sn": NetworkUtils.INVALID_MAC}
RTU_CONFIG = {**RTU_ARGS, "sn": "N/A"}
SOLARMAN_CONFIG = {**SOLARMAN_ARGS, "sn": 1234567890}
SUNSPEC_CONFIG = {**SUNSPEC_ARGS, "sn": "SUNSPEC135792468"}
P1_TELNET_CONFIG = {**P1_TELNET_ARGS, "meter_serial_number": "abc5qwerty"}
