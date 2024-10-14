TCP_CONFIG = {
    "connection": "TCP",
    "host": "localhost",
    "mac": "00:00:00:00:00:00",
    "port": 502,
    "type": "solaredge",
    "address": 4,
}

RTU_CONFIG = {
    "connection": "RTU",
    "port": "/dev/ttyS0",
    "baudrate": 9600,
    "bytesize": 8,
    "parity": "N",
    "stopbits": 1,
    "type": "lqt40s",
    "address": 1,
}

SOLARMAN_CONFIG = {
    "connection": "SOLARMAN",
    "host": "localhost",
    "mac": "00:00:00:00:00:00",
    "serial": 1234567890,
    "port": 502,
    "type": "deye",
    "address": 1
}

SUNSPEC_CONFIG = {
    "connection": "SUNSPEC",
    "host": "localhost",
    "mac": "00:00:00:00:00:00",
    "port": 502,
    "address": 1
}