import pytest
from unittest.mock import MagicMock
from server.web.handler.requestData import RequestData
from server.web.handler.get.modbus import RegisterHandler, HoldingHandler, InputHandler  # adapt to your actual module import
from server.blackboard import BlackBoard
import json
import struct

@pytest.fixture
def inverter_fixture():
    inverter = MagicMock()

    # These registers are word-sized, so they are 2 bytes each, e.g. the 1 in [1, 2, 3, 4] is 0x0100 (2 bytes) in hex (little endian)
    inverter.readHoldingRegister.return_value = [1, 2, 3, 4]
    inverter.readInputRegister.return_value = [0x0A, 0x0B, 0x0C, 0x0D]
    return inverter

@pytest.fixture
def request_data():
    bb = BlackBoard()
    inv = MagicMock()
    bb.inverters.add(inv)

    def readHoldingRegister(address, size):
        return [i for i in range(address, address + size)]
    
    def readInputRegister(address, size):
        return [0x0A + i for i in range(address, address + size)]

    inv.readHoldingRegisters = readHoldingRegister
    inv.readInputRegisters = readInputRegister

    post_params = {'address': '1'}
    query_params = {'type': 'uint', 'size':'2', 'endianess':'big'}
    return RequestData(bb, post_params, query_params, {}, None)

def test_HoldingHandler(request_data):
    handler = HoldingHandler()
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response.get('register') == 1
    assert response.get('raw_value') == '00010002'
    assert response.get('value') == 65538  # = 0x00010002 in uint

def test_InputHandler(request_data):
    handler = InputHandler()
    request_data.post_params['address'] = 0
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    
    assert response.get('register') == 0
    assert response.get('raw_value') == '000a000b'
    assert response.get('value') == 655371 # = 0x000a000b in uint

def test_missing_address(inverter_fixture):
    handler = HoldingHandler()

    bb = BlackBoard()
    bb.inverters.add(inverter_fixture)

    request_data = RequestData(bb, {}, {}, {}, None)
    status_code, response = handler.doGet(request_data)
    assert status_code == 400
    assert json.loads(response).get('error') == 'missing address'

def test_inverter_not_initialized():
    handler = HoldingHandler()
    request_data = RequestData(BlackBoard(), {'address': '0'}, {}, {}, None)
    status_code, response = handler.doGet(request_data)
    assert status_code == 400
    assert json.loads(response).get('error') == 'inverter not initialized'


def test_unknown_datatype(request_data):
    handler = HoldingHandler()
    request_data.query_params['type'] = 'unknown'
    status_code, response = handler.doGet(request_data)
    assert status_code == 400
    assert 'Unsupported datatype' in json.loads(response).get('error')

def test_invalid_endianess(request_data):
    handler = HoldingHandler()
    request_data.query_params['endianess'] = 'wrong_endianess'
    status_code, response = handler.doGet(request_data)
    assert status_code == 400
    assert 'Unsupported endianess' in json.loads(response).get('error')

def test_invalid_size(request_data):
    handler = HoldingHandler()
    request_data.query_params['size'] = '10'

    def readHoldingRegister(address, size):
        raise Exception('invalid or incomplete address range')

    request_data.bb.inverters.lst[0].readHoldingRegisters = readHoldingRegister
    status_code, response = handler.doGet(request_data)
    assert status_code == 400
    assert json.loads(response).get('error') == 'invalid or incomplete address range'

def test_uint_value(request_data):
    handler = HoldingHandler()
    request_data.query_params['type'] = 'uint'
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response.get('value') == 65538  # = 0x00010002 in uint

def test_int_value(request_data):
    handler = HoldingHandler()
    request_data.query_params['type'] = 'int'
    request_data.query_params['size'] = '2'
    request_data.post_params['address'] = '3'
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response.get('value') == 196612  # = 0x00030004 as signed int

def test_float_value_little(request_data):
    handler = HoldingHandler()
    request_data.query_params['type'] = 'float'
    request_data.query_params['size'] = '2'
    request_data.query_params['endianess'] = 'little'
    
    request_data.bb.inverters.lst[0].readHoldingRegisters = lambda address, size: [0x147b, 0x4248] # 50.02 as little endian float

    status_code, response = handler.doGet(request_data)

    assert status_code == 200
    response = json.loads(response)
    
    val = response.get('value') - 199148.3125

    # Can't use assert equals on floating point numbers due to precision issues
    assert abs(val) < 1e-20
    

def test_float_value_big(request_data):
    handler = HoldingHandler()
    request_data.query_params['type'] = 'float'
    request_data.query_params['size'] = '2'
    request_data.query_params['endianess'] = 'big'

    request_data.bb.inverters.lst[0].readHoldingRegisters = lambda address, size: [0x147b, 0x4248]     # 7.69925e+35 as big endian float

    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    # Can't use assert equals on floating point numbers due to precision issues
    val = response.get('value') - 1.2685333253188879e-26
    assert abs(val) < 1e-5
    
def test_double_value(request_data):
    #request_data.stats['inverter'].readHoldingRegisters.return_value = {i: bytes([i]) for i in range(8)} 
    # This creates a dictionary where each key is an address and each value is one byte, with values from 0 to 7.
    handler = HoldingHandler()
    request_data.query_params['type'] = 'float'
    request_data.query_params['size'] = '4'
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    result = response.get('value')    # round to ensure accurate comparison of floating points
    expected = struct.unpack('>d', bytes(range(1, 9)))[0]
    assert round(result, 9) == round(expected, 9)   # or whatever level of precision is appropriate  