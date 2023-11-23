import pytest
from unittest.mock import MagicMock
from server.web.handler.requestData import RequestData
from server.web.handler.get.modbus import RegisterHandler, HoldingHandler, InputHandler  # adapt to your actual module import
import json

@pytest.fixture
def inverter_fixture():
    inverter = MagicMock()
    inverter.readHoldingRegisters.return_value = {0: b'\x01', 1: b'\x02', 2: b'\x03', 3: b'\x04'}
    inverter.readInputRegisters.return_value = {0: b'\x0A', 1: b'\x0B', 2: b'\x0C', 3: b'\x0D'}
    return inverter

@pytest.fixture
def request_data():
    stats = {'inverter': MagicMock()}
    stats['inverter'].readHoldingRegisters.return_value = {0: b'\x01', 1: b'\x02', 2: b'\x03', 3: b'\x04'}
    stats['inverter'].readInputRegisters.return_value = {0: b'\x0A', 1: b'\x0B', 2: b'\x0C', 3: b'\x0D'}

    post_params = {'address': '0'}
    query_params = {'type': 'uint', 'size':'4', 'endianess':'big'}
    return RequestData(stats, post_params, query_params, {}, None, None, None)

def test_HoldingHandler(request_data):
    handler = HoldingHandler()
    status_code, response = handler.doGet(request_data)
    assert status_code == 200
    response = json.loads(response)
    assert response.get('register') == 0
    assert response.get('raw_value') == '01020304'
    assert response.get('value') == 16909060  # = 0x01020304 in uint

def test_InputHandler(request_data):
    handler = InputHandler()
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

def test_invalid_address_range(inverter_fixture):
    handler = HoldingHandler()
    request_data = RequestData({'inverter': inverter_fixture}, {'address': '5'}, {}, {}, None, None, None)
    status_code, response = handler.doGet(request_data)
    assert status_code == 400
    assert json.loads(response).get('error') == 'invalid or incomplete address range'

def test_unknown_datatype(request_data):
    handler = HoldingHandler()
    request_data.query_params['type'] = 'unknown'
    status_code, response = handler.doGet(request_data)
    assert status_code == 400
    assert json.loads(response).get('error') == 'Unknown datatype'

def test_invalid_endianess(request_data):
    handler = HoldingHandler()
    request_data.query_params['endianess'] = 'wrong_endianess'
    status_code, response = handler.doGet(request_data)
    assert status_code == 400
    assert json.loads(response).get('error') == 'Invalid endianess. endianess must be big or little'

def test_invalid_size(request_data):
    handler = HoldingHandler()
    request_data.query_params['size'] = '10'
    status_code, response = handler.doGet(request_data)
    assert status_code == 400
    assert json.loads(response).get('error') == 'invalid or incomplete address range'