from unittest.mock import MagicMock
from server.inverters.InverterTCP import InverterTCP

from server.inverters.supported_inverters import profiles as p

from server.inverters.supported_inverters.inverters.sungrow import profile as SUNGROW

inverter_name = SUNGROW['name']

def test_read_harvest_data():
    inv = InverterTCP(("localhost", 8081, inverter_name, 1))

    
    inv.client = MagicMock()
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