from io import BytesIO
from unittest.mock import patch
from server.web.server import Server, request_handler_factory, Endpoints
from http.server import BaseHTTPRequestHandler
import pytest
import json

import server.crypto.crypto as crypto

from server.blackboard import BlackBoard

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


@patch.object(BaseHTTPRequestHandler, "finish")
@patch.object(BaseHTTPRequestHandler, "handle")
@patch.object(BaseHTTPRequestHandler, "setup")
def test_handler_api_get_enpoints_params(mock_setup, mock_handle, mock_finish):
    h = Endpoints()
    path, query = h.pre_do("/api/inverter/modbus/holding/1234?test=hello")

    # this could really be any handler
    from server.web.handler.get.modbus_read import HoldingHandler
    handlers = {"inverter/modbus/holding/{address}": HoldingHandler()}

    handler, params = h.get_api_handler(path, "/api/", h.convert_keys_to_regex(handlers))
    assert handler is not None
    assert params is not None
    assert hasattr(handler, "do_get")
    assert params["address"] == "1234"
    assert query["test"] == "hello"


def test_open_close():
    s = Server(("localhost", 8081), BlackBoard())
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
def test_handler_get_root(mock_setup, mock_handle, mock_finish):
    # test that the root handler is used when no other handler matches
    h = request_handler_factory(BlackBoard())(None, None, None)

    # we need to mock the base class methods
    h.path = ""
    h.send_response = lambda x: None
    h.send_header = lambda x, y: None
    h.end_headers = lambda: None
    h.wfile = BytesIO()

    with patch("server.crypto.crypto.HardwareCrypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.HardwareCrypto.atcab_read_serial_number", return_value=(crypto.ATCA_SUCCESS, b'123456789012')):
            h.do_GET()
    v = h.wfile.getvalue().decode("utf-8")
    assert "<html>" in v

@patch.object(BaseHTTPRequestHandler, "finish")
@patch.object(BaseHTTPRequestHandler, "handle")
@patch.object(BaseHTTPRequestHandler, "setup")
def test_handler_get_returns_exception(mock_setup, mock_handle, mock_finish):
    # test that exceptions are handled and retuns an exception message
    h = request_handler_factory(BlackBoard())(None, None, None)

    # we need to mock the base class methods
    h.path = "/api/crypto"
    h.send_response = lambda x: None
    h.send_header = lambda x, y: None
    h.end_headers = lambda: None
    h.wfile = BytesIO()

    with patch("server.crypto.crypto.HardwareCrypto.atcab_init", side_effect=Exception("test")), patch('server.crypto.software.SoftwareCrypto.atcab_init', side_effect=Exception("test")):
        h.do_GET()
    v = h.wfile.getvalue().decode("utf-8")
    assert "test" in v
    assert "exception" in v

@patch.object(BaseHTTPRequestHandler, "finish")
@patch.object(BaseHTTPRequestHandler, "handle")
@patch.object(BaseHTTPRequestHandler, "setup")
def test_hanler_post_returns_exception(mock_setup, mock_handle, mock_finish):
    h = request_handler_factory(BlackBoard())(None, None, None)

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
def test_handler_get_do_get(mock_setup, mock_handle, mock_finish):
    # check that all get handlers have a doGet method
    h = request_handler_factory(BlackBoard())(None, None, None)
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
def test_handler_get_do_post(mock_setup, mock_handle, mock_finish):
    # check that all post handlers have a doPost method
    h = request_handler_factory(BlackBoard())(None, None, None)
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
def test_handler_get_do_delete(mock_setup, mock_handle, mock_finish):
    # check that all post handlers have a doPost method
    h = request_handler_factory(BlackBoard())(None, None, None)
    for handler in h.endpoints.api_delete.values():
        assert hasattr(handler, "do_delete")
        assert hasattr(handler, "schema")
        assert handler.schema() is not None
        try:
            json.dumps(handler.schema())
        except Exception:
            raise AssertionError("Failed to json.dumps schema for {}".format(handler))
