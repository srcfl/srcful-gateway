from unittest.mock import MagicMock
from server.inverters.InverterTCP import InverterTCP
from server.inverters.InverterRTU import InverterRTU 
from server.inverters.supported_inverters.profiles import InverterProfiles
import pytest

profiles = InverterProfiles()
sungrow = profiles.get("sungrow")


def get_inverters():
    inv_tcp = InverterTCP(("localhost", 8081, sungrow.name, 1))
    inv_rtu = InverterRTU(("/dev/ttyUSB0", 9600, 8, "N", 1, sungrow.name, 1))

    return [inv_tcp, inv_rtu]


def test_get_tcp_config():
    inv = InverterTCP(("localhost", 8081, sungrow.name, 1))

    assert inv.get_config_dict() == {
        "connection": "TCP",
        "type": "sungrow",
        "address": 1,
        "host": "localhost",
        "port": 8081,
    }


def test_get_rt_config():
    inv = InverterRTU(("/dev/ttyUSB0", 9600, 8, "N", 1, sungrow.name, 1))

    assert inv.get_config_dict() == { 
        "connection": "RTU",
        "type": "sungrow",
        "address": 1,
        "host": "/dev/ttyUSB0",
        "baudrate": 9600,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1
    }


def test_inverter_clone():
    inverters = get_inverters()

    for inv in inverters:
        assert inv.setup == inv.clone().setup


def test_read_harvest_data():
    inverters = get_inverters()

    for inv in inverters:

        inv.open(reconnect_delay=0, retries=0, timeout=0.1, reconnect_delay_max=0)
        inv.get_address = MagicMock(return_value=1)

        def read_registers(address, size, slave):
            class Ret:
                def __init__(self):
                    self.registers = [i for i in range(address, address + size)]

            return Ret()

        inv.client.read_holding_registers = read_registers
        inv.client.read_input_registers = read_registers

        result = inv.read_harvest_data()
        assert type(result) is dict
        assert 4999 in result
        assert 5112 in result
        assert len(result) == 110 + 50


def test_is_terminated():
    inverters = get_inverters()

    for inv in inverters:
        inv.open(reconnect_delay=0, retries=0, timeout=0.1, reconnect_delay_max=0)
        
        assert not inv.is_terminated()

        inv.terminate()

        assert inv.is_terminated()


def test_raises_exception():
    inverters = get_inverters()

    for inv in inverters:
        inv.open(reconnect_delay=0, retries=0, timeout=0.1, reconnect_delay_max=0)

        inv.terminate()

        with pytest.raises(Exception):
            inv.read_harvest_data()


