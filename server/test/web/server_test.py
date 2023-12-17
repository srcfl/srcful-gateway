from io import BytesIO
from unittest.mock import patch
from server.web.server import Server, requestHandlerFactory
from http.server import BaseHTTPRequestHandler
import pytest

from http.server import HTTPServer


def timeFunc():
  return 0


def getChipInfoFunc():
  return "testymctestface"


@pytest.fixture
def mock_handle():
  pass


@pytest.fixture
def mock_setup():
  pass


@pytest.fixture
def mock_finish():
  pass


@patch.object(BaseHTTPRequestHandler, 'finish')
@patch.object(BaseHTTPRequestHandler, 'handle')
@patch.object(BaseHTTPRequestHandler, 'setup')
def test_handler_apiGetEnpoints(mock_setup, mock_handle, mock_finish):
  h = requestHandlerFactory(None, None, None, None)(None, None, None)
  handler, params = h.getAPIHandler('/api/crypto', '/api/', h.api_get)
  assert handler != None
  assert hasattr(handler, 'doGet')

@patch.object(BaseHTTPRequestHandler, 'finish')
@patch.object(BaseHTTPRequestHandler, 'handle')
@patch.object(BaseHTTPRequestHandler, 'setup')
def test_handler_apiGetEnpointsParams(mock_setup, mock_handle, mock_finish):
  h = requestHandlerFactory(None, None, None, None)(None, None, None)
  path, query = h.pre_do('/api/inverter/modbus/holding/1234?test=hello')
  handler, params = h.getAPIHandler(path, '/api/', h.api_get)
  assert handler != None
  assert params != None
  assert hasattr(handler, 'doGet')
  assert params['address'] == '1234'
  assert query['test'] == 'hello'


def test_open_close():
  s = Server(('localhost', 8081), {}, timeFunc, getChipInfoFunc)
  assert isinstance(s._webServer, HTTPServer)
  s.close()
  assert s._webServer is None


def test_handler_postBytest2Dict():
  h = requestHandlerFactory(None, None, None, None)
  d = h.post2Dict('')
  assert d == {}
  assert h.post2Dict('foo') == {}
  assert h.post2Dict('foo=') == {'foo': ''}
  assert h.post2Dict('foo=bar') == {'foo': 'bar'}
  assert h.post2Dict('foo=bar&baz=qux') == {'foo': 'bar', 'baz': 'qux'}
  assert h.post2Dict('name=John%20Doe&age=30&location=New%20York') == {
      'name': 'John Doe', 'age': '30', 'location': 'New York'}


def test_handler_getPostdata():
  h = requestHandlerFactory(None, None, None, None)
  assert h.getData({'Content-Length': '0'}, BytesIO(b'')) == {}

  data = b'name=John%20Doe&age=30&location=New%20York'
  assert h.getData({'Content-Length': len(data)}, BytesIO(data)
                   ) == {'name': 'John Doe', 'age': '30', 'location': 'New York'}

  data = b'{"name": "John Doe", "age": 30, "location": "New York"}'
  assert h.getData({'Content-Length': len(data)}, BytesIO(data)
                   ) == {'name': 'John Doe', 'age': 30, 'location': 'New York'}

  data = b'{"name": "John&Doe", "age": 30, "location": "New York = Kalmar"}'
  assert h.getData({'Content-Length': len(data)}, BytesIO(data)
                   ) == {'name': 'John&Doe', 'age': 30, 'location': 'New York = Kalmar'}

@patch.object(BaseHTTPRequestHandler, 'finish')
@patch.object(BaseHTTPRequestHandler, 'handle')
@patch.object(BaseHTTPRequestHandler, 'setup')
def test_handler_get_root(mock_setup, mock_handle, mock_finish):
  # test that the root handler is used when no other handler matches
  h = requestHandlerFactory({"startTime": 7, "name":"dret"}, lambda: 10, lambda: "crypto dret", [])(None, None, None)

  # we need to mock the base class methods
  h.path = ""
  h.send_response = lambda x: None
  h.send_header = lambda x, y: None
  h.end_headers = lambda: None
  h.wfile = BytesIO()

  h.do_GET()
  v = h.wfile.getvalue().decode("utf-8")
  assert "<html>" in v

@patch.object(BaseHTTPRequestHandler, 'finish')
@patch.object(BaseHTTPRequestHandler, 'handle')
@patch.object(BaseHTTPRequestHandler, 'setup')
def test_handler_get_doGet(mock_setup, mock_handle, mock_finish):
  # check that all get handlers have a doGet method
  h = requestHandlerFactory({"startTime": 7, "name":"dret"}, lambda: 10, lambda: "crypto dret", [])(None, None, None)
  for handler in h.api_get.values():
    assert hasattr(handler, 'doGet')

@patch.object(BaseHTTPRequestHandler, 'finish')
@patch.object(BaseHTTPRequestHandler, 'handle')
@patch.object(BaseHTTPRequestHandler, 'setup')
def test_handler_get_doPost(mock_setup, mock_handle, mock_finish):
  # check that all post handlers have a doPost method
  h = requestHandlerFactory({"startTime": 7, "name":"dret"}, lambda: 10, lambda: "crypto dret", [])(None, None, None)
  for handler in h.api_post.values():
    assert hasattr(handler, 'doPost')
