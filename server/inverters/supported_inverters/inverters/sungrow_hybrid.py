profile = {
    "name": "sungrow_hybrid",
    "registers": [
        {
            "operation": 0x04,
            "start_register": 4999,
            "num_of_registers": 110
        },
        {
            "operation": 0x04,
            "start_register": 5112,
            "num_of_registers": 50
        },
        {
            "operation": 0x04,
            "start_register": 13000,
            "num_of_registers": 6
        },
        {
            "operation": 0x04,
            "start_register": 13028,
            "num_of_registers": 6
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
