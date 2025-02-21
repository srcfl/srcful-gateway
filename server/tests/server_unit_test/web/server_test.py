from http import HTTPStatus
from io import BytesIO
from unittest.mock import Mock, patch
from server.crypto.crypto_state import CryptoState
from server.web.server import Server, request_handler_factory, Endpoints
from http.server import BaseHTTPRequestHandler
import pytest
import json

import server.crypto.crypto as crypto

from server.app.blackboard import BlackBoard

from http.server import HTTPServer


def time_func():
    return 0


def get_chip_info_func():
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


@pytest.fixture
def bb():
    return BlackBoard(Mock(spec=CryptoState))


@patch.object(BaseHTTPRequestHandler, "finish")
@patch.object(BaseHTTPRequestHandler, "handle")
@patch.object(BaseHTTPRequestHandler, "setup")
def test_handler_api_get_enpoints_params(mock_setup, mock_handle, mock_finish):
    h = Endpoints()
    path, query = h.pre_do("/api/inverter/modbus?address=1234&device_id=00.00.00.00.00.00&function_code=0x03&size=1&type=U16&endianess=big")

    # this could really be any handler
    from server.web.handler.get.modbus import ModbusHandler
    handlers = {"inverter/modbus": ModbusHandler()}

    handler, params = h.get_api_handler(path, "/api/", h.convert_keys_to_regex(handlers))
    assert handler is not None
    assert params is not None
    assert hasattr(handler, "do_get")
    assert query["address"] == "1234"
    assert query["device_id"] == "00.00.00.00.00.00"
    assert query["function_code"] == "0x03"
    assert query["size"] == "1"
    assert query["type"] == "U16"
    assert query["endianess"] == "big"


def test_open_close(bb: BlackBoard):
    s = Server(("localhost", 8081), bb)
    assert isinstance(s._web_server, HTTPServer)
    s.close()
    assert s._web_server is None


def test_handler_post_bytest_2_dict():
    h = Endpoints()
    d = h.post_2_dict("")
    assert d == {}
    assert h.post_2_dict("foo") == {}
    assert h.post_2_dict("foo=") == {"foo": ""}
    assert h.post_2_dict("foo=bar") == {"foo": "bar"}
    assert h.post_2_dict("foo=bar&baz=qux") == {"foo": "bar", "baz": "qux"}
    assert h.post_2_dict("name=John%20Doe&age=30&location=New%20York") == {
        "name": "John Doe",
        "age": "30",
        "location": "New York",
    }


def test_handler_get_post_data():
    h = Endpoints()
    assert h.get_data({"Content-Length": "0"}, BytesIO(b"")) == {}

    data = b"name=John%20Doe&age=30&location=New%20York"
    assert h.get_data({"Content-Length": len(data)}, BytesIO(data)) == {
        "name": "John Doe",
        "age": "30",
        "location": "New York",
    }

    data = b'{"name": "John Doe", "age": 30, "location": "New York"}'
    assert h.get_data({"Content-Length": len(data)}, BytesIO(data)) == {
        "name": "John Doe",
        "age": 30,
        "location": "New York",
    }

    data = b'{"name": "John&Doe", "age": 30, "location": "New York = Kalmar"}'
    assert h.get_data({"Content-Length": len(data)}, BytesIO(data)) == {
        "name": "John&Doe",
        "age": 30,
        "location": "New York = Kalmar",
    }


@patch.object(BaseHTTPRequestHandler, "finish")
@patch.object(BaseHTTPRequestHandler, "handle")
@patch.object(BaseHTTPRequestHandler, "setup")
def test_handler_get_root_not_found(mock_setup, mock_handle, mock_finish, bb: BlackBoard):
    h = request_handler_factory(bb)(None, None, None)

    # Mock send_response to capture the status code
    h.send_response = Mock()
    h.send_header = Mock()
    h.end_headers = Mock()
    h.wfile = BytesIO()

    with patch("server.crypto.crypto.HardwareCrypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.HardwareCrypto.atcab_read_serial_number", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            h.path = "some_path_that_does_not_exist"
            h.do_GET()

    # Check that send_response was called with 404
    h.send_response.assert_called_once_with(404)
    v = h.wfile.getvalue().decode("utf-8")
    assert "<html>" not in v


@patch.object(BaseHTTPRequestHandler, "finish")
@patch.object(BaseHTTPRequestHandler, "handle")
@patch.object(BaseHTTPRequestHandler, "setup")
def test_handler_get_no_path_returns_root(mock_setup, mock_handle, mock_finish, bb: BlackBoard):
    h = request_handler_factory(bb)(None, None, None)

    # Mock send_response to capture the status code
    h.send_response = Mock()
    h.send_header = Mock()
    h.end_headers = Mock()
    h.wfile = BytesIO()

    # Set up the crypto state mock
    mock_crypto_state = Mock(spec=CryptoState)
    mock_crypto_state.to_dict.return_value = {
        'deviceName': 'test_device',
        'serialNumber': '123456789',
        'publicKey': 'abcdef',
        'compactKey': 'compact',
        'chipDeathCount': '0'
    }
    bb._crypto_state = mock_crypto_state
    # Set individual components that make up the state
    bb._start_time = 0  # This affects uptime
    bb._devices.saved = []  # Set saved devices to empty list

    with patch("server.crypto.crypto.HardwareCrypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.HardwareCrypto.atcab_read_serial_number", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            h.path = ""
            h.do_GET()

    # Verify the response was sent
    h.send_response.assert_called_once_with(200)
    assert h.wfile.getvalue() != b""


@patch.object(BaseHTTPRequestHandler, "finish")
@patch.object(BaseHTTPRequestHandler, "handle")
@patch.object(BaseHTTPRequestHandler, "setup")
def test_handler_get_returns_exception(mock_setup, mock_handle, mock_finish, bb: BlackBoard):
    # test that exceptions are handled and retuns an exception message
    h = request_handler_factory(bb)(None, None, None)

    # we need to mock the base class methods
    h.path = "/api/crypto"
    bb._crypto_state.to_dict.side_effect = Exception("test")
    h.send_response = lambda x: None
    h.send_header = lambda x, y: None
    h.end_headers = lambda: None
    h.wfile = BytesIO()

    h.do_GET()
    v = h.wfile.getvalue().decode("utf-8")
    assert "test" in v
    assert "exception" in v


@patch.object(BaseHTTPRequestHandler, "finish")
@patch.object(BaseHTTPRequestHandler, "handle")
@patch.object(BaseHTTPRequestHandler, "setup")
def test_hanler_post_returns_exception(mock_setup, mock_handle, mock_finish, bb: BlackBoard):
    h = request_handler_factory(bb)(None, None, None)

    # we need to mock the base class methods
    h.path = "/api/echo"
    h.send_response = lambda x: None
    h.send_header = lambda x, y: None
    h.end_headers = lambda: None
    h.headers = {"Content-Length": 0}
    h.wfile = BytesIO()
    h.rfile = BytesIO()

    with patch("server.web.handler.post.echo.Handler.do_post", side_effect=Exception("test")):
        h.do_POST()
    v = h.wfile.getvalue().decode("utf-8")
    assert "test" in v
    assert "exception" in v


@patch.object(BaseHTTPRequestHandler, "finish")
@patch.object(BaseHTTPRequestHandler, "handle")
@patch.object(BaseHTTPRequestHandler, "setup")
def test_handler_get_do_get(mock_setup, mock_handle, mock_finish, bb: BlackBoard):
    # check that all get handlers have a doGet method
    h = request_handler_factory(bb)(None, None, None)
    for handler in h.endpoints.api_get.values():
        assert hasattr(handler, "do_get")
        assert hasattr(handler, "schema")
        assert handler.schema() is not None
        try:
            json.dumps(handler.schema())
        except Exception:
            raise AssertionError("Failed to json.dumps schema for {}".format(handler))


@patch.object(BaseHTTPRequestHandler, "finish")
@patch.object(BaseHTTPRequestHandler, "handle")
@patch.object(BaseHTTPRequestHandler, "setup")
def test_handler_get_do_post(mock_setup, mock_handle, mock_finish, bb: BlackBoard):
    # check that all post handlers have a doPost method
    h = request_handler_factory(bb)(None, None, None)
    for handler in h.endpoints.api_post.values():
        assert hasattr(handler, "do_post")
        assert hasattr(handler, "schema")
        assert handler.schema() is not None
        try:
            json.dumps(handler.schema())
        except Exception:
            raise AssertionError("Failed to json.dumps schema for {}".format(handler))


@patch.object(BaseHTTPRequestHandler, "finish")
@patch.object(BaseHTTPRequestHandler, "handle")
@patch.object(BaseHTTPRequestHandler, "setup")
def test_handler_get_do_delete(mock_setup, mock_handle, mock_finish, bb: BlackBoard):
    # check that all post handlers have a doPost method
    h = request_handler_factory(bb)(None, None, None)
    for handler in h.endpoints.api_delete.values():
        assert hasattr(handler, "do_delete")
        assert hasattr(handler, "schema")
        assert handler.schema() is not None
        try:
            json.dumps(handler.schema())
        except Exception:
            raise AssertionError("Failed to json.dumps schema for {}".format(handler))
