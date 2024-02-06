profile = {
    "name": "sungrow_hybrid",
    "registers": [
    {
        "operation": 0x04,
        "scanStart": 4999,
        "scanRange": 110
    },
    {
        "operation":0x04,
        "scanStart": 5112,
        "scanRange": 50
    },
    {
        "operation":0x04,
        "scanStart": 13000,
        "scanRange": 6
    },
    {
        "operation":0x04,
        "scanStart": 13028,
        "scanRange": 6
    }
    ],
    "controlRegister": {
        "enableControl": {
            "address": 30099,
            "type": "uint16",
            "unit": "-",
            "description": "1 or 0 to enable or disable the inverter."
        },
        "activePower": {
            "address": 30100,
            "type": "uint16",
            "unit": "W",
            "description": "Active power output of the inverter."
        }
    }
}