TCP_CONFIG = {
    "connection": "TCP",
    "ip": "localhost",
    "mac": "00:00:00:00:00:00",
    "port": 502,
    "device_type": "solaredge",
    "slave_id": 4,
}

RTU_CONFIG = {
    "connection": "RTU",
    "port": "/dev/ttyS0",
    "baudrate": 9600,
    "bytesize": 8,
    "parity": "N",
    "stopbits": 1,
    "device_type": "lqt40s",
    "slave_id": 1,
}

SOLARMAN_CONFIG = {
    "connection": "SOLARMAN",
    "ip": "localhost",
    "mac": "00:00:00:00:00:00",
    "serial": 1234567890,
    "port": 502,
    "device_type": "deye",
    "slave_id": 1,
    "verbose": True
}

SUNSPEC_CONFIG = {
    "connection": "SUNSPEC",
    "ip": "localhost",
    "mac": "00:00:00:00:00:00",
    "port": 502,
    "slave_id": 1
}