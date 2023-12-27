import pytest
from unittest.mock import MagicMock
from server.web.handler.requestData import RequestData
from server.web.handler.get.modbus import RegisterHandler, HoldingHandler, InputHandler  # adapt to your actual module import
import json
import struct

@pytest.fixture
def inverter_fixture():
    inverter = MagicMock()
    inverter.readHoldingRegister.return_value = [1, 2, 3, 4]
    inverter.readInputRegister.return_value = [0x0A, 0x0B, 0x0C, 0x0D]
    return inverter

@pytest.fixture
def request_data():
    stats = {'inverter': MagicMock()}

    def readHoldingRegister(address, size):
        return [i for i in range(address, address + size)]
    
    def readInputRegister(address, size):
        return [0x0A + i for i in range(address, address + size)]

    stats['inverter'].readHoldingRegister = readHoldingRegister
    stats['inverter'].readInputRegister = readInputRegister

    post_params = {'address': '1'}
    query_params = {'type': 'uint', 'size':'4', 'endianess':'big'}
    return RequestData(stats, post_params, query_params, {}, None, None, None)

def test_HoldingHandler(request_data):
    handler = HoldingHandler()
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response.get('register') == 1
    assert response.get('raw_value') == '01020304'
    assert response.get('value') == 16909060  # = 0x01020304 in uint

def test_InputHandler(request_data):
    handler = InputHandler()
    request_data.post_params['address'] = 0
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    
    assert response.get('register') == 0
    assert response.get('raw_value') == '0a0b0c0d'
    assert response.get('value') == 168496141  # = 0x0A0B0C0D in uint

def test_missing_address(inverter_fixture):
    handler = HoldingHandler()
    request_data = RequestData({'inverter': inverter_fixture}, {}, {}, {}, None, None, None)
    status_code, response = handler.doGet(request_data)
    assert status_code == 400
    assert json.loads(response).get('error') == 'missing address'

def test_inverter_not_initialized():
    handler = HoldingHandler()
    request_data = RequestData({}, {'address': '0'}, {}, {}, None, None, None)
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

    request_data.stats['inverter'].readHoldingRegister = readHoldingRegister
    status_code, response = handler.doGet(request_data)
    assert status_code == 400
    assert json.loads(response).get('error') == 'invalid or incomplete address range'

def test_uint_value(request_data):
    handler = HoldingHandler()
    request_data.query_params['type'] = 'uint'
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response.get('value') == 16909060  # = 0x01020304 as unsigned int

def test_int_value(request_data):
    handler = HoldingHandler()
    request_data.query_params['type'] = 'int'
    request_data.query_params['size'] = '2'
    request_data.post_params['address'] = '3'
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response.get('value') == 772  # = 0x0304 as signed int

def test_float_value_little(request_data):
    handler = HoldingHandler()
    request_data.query_params['type'] = 'float'
    request_data.query_params['size'] = '4'
    request_data.query_params['endianess'] = 'little'
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    # Can't use assert equals on floating point numbers due to precision issues
    assert abs(response.get('value') - 1.53998961e-36) < 1e-20  # value = 0x01020304 as little endian float (1.53998961e-36)

def test_float_value_big(request_data):
    handler = HoldingHandler()
    request_data.query_params['type'] = 'float'
    request_data.query_params['size'] = '4'
    request_data.query_params['endianess'] = 'big'

    request_data.stats['inverter'].readHoldingRegister = lambda address, size: [0x41, 0x89, 0x5c, 0x29]     # 17.17 as big endian float

    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    # Can't use assert equals on floating point numbers due to precision issues
    assert abs(response.get('value') -17.17) < 1e-5  # value = 0x01020304 as big endian float (2.38793926e-38)

def test_ascii_value(request_data):
    handler = HoldingHandler()
    expected = 'Hello World!'
    request_data.query_params['type'] = 'ascii'
    request_data.query_params['size'] = len(expected)

    request_data.stats['inverter'].readHoldingRegister = lambda address, size: [ord(i) for i in expected]

    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response.get('value') == expected  # = 0x0102 as ASCII

def test_utf16_value_big(request_data):
    handler = HoldingHandler()
    expected = 'Hello World!'
    request_data.query_params['type'] = 'utf16'
    request_data.query_params['size'] = '2'
    encoded = expected.encode("utf-16be")
    request_data.stats['inverter'].readHoldingRegister = lambda address, size: encoded    # normal ascii characters are 1 byte in utf16

    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    # = 0x0102 as utf16. Could not compare with direct value due to difference in utf16 encoding in python string depending on sys.byte_order
    assert response.get('value') == expected

def test_utf16_value_little(request_data):
    handler = HoldingHandler()
    expected = 'Hello World!'
    request_data.query_params['type'] = 'utf16'
    request_data.query_params['size'] = '2'
    request_data.query_params['endianess'] = 'little'
    encoded = expected.encode("utf-16le")
    request_data.stats['inverter'].readHoldingRegister = lambda address, size: encoded    # normal ascii characters are 1 byte in utf16

    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    # = 0x0102 as utf16. Could not compare with direct value due to difference in utf16 encoding in python string depending on sys.byte_order
    assert response.get('value') == expected
    
def test_double_value(request_data):
    #request_data.stats['inverter'].readHoldingRegisters.return_value = {i: bytes([i]) for i in range(8)} 
    # This creates a dictionary where each key is an address and each value is one byte, with values from 0 to 7.
    handler = HoldingHandler()
    request_data.query_params['type'] = 'float'
    request_data.query_params['size'] = '8'
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    result = response.get('value')    # round to ensure accurate comparison of floating points
    expected = struct.unpack('>d', bytes(range(1, 9)))[0]
    assert round(result, 9) == round(expected, 9)   # or whatever level of precision is appropriate  