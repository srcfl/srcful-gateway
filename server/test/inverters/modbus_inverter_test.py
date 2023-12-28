import pytest
import json
from unittest.mock import MagicMock
from server.inverters.inverter import Inverter
from server.inverters.inverter_types import INVERTERS, SUNGROW

def test_readHarvestData():
    inv = Inverter()

    inv.registers = INVERTERS[SUNGROW]
    inv.client = MagicMock()
    inv.getAddress = MagicMock(return_value=1)

    def readRegisters(address, size, slave):
        class Ret():
            def __init__(self):
                self.registers = [i for i in range(address, address + size)]

        return Ret()
    
    inv.client.read_holding_registers = readRegisters
    inv.client.read_input_registers = readRegisters

    result = inv.readHarvestData()
    assert type(result) == dict
    assert 4999 in result
    assert 5112 in result
    assert len(result) == 110 + 50
