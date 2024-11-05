import pytest
from unittest.mock import patch, MagicMock
import json
import datetime
from server.web.handler.post.crypto_sign import Handler
from server.web.handler.requestData import RequestData
from server.blackboard import BlackBoard
from server.crypto import crypto

@pytest.fixture
def handler():
    return Handler()

@pytest.fixture
def mock_request_data():
    bb = BlackBoard()
    return RequestData(bb, {}, {}, {})

@pytest.fixture
def mock_chip():
    chip = MagicMock()
    chip.get_serial_number.return_value = bytes.fromhex('f42ea576ac87184445')
    chip.get_signature.return_value = bytes.fromhex('a' * 128)
    return chip

def test_schema(handler):
    """Test schema returns correct structure"""
    schema = handler.schema()
    assert schema["type"] == "post"
    assert "description" in schema
    assert "optional" in schema
    assert "returns" in schema

def test_json_schema(handler):
    """Test json_schema returns valid JSON"""
    schema_json = handler.json_schema()
    assert isinstance(schema_json, str)
    parsed = json.loads(schema_json)
    assert parsed["type"] == "post"

def test_construct_message_with_no_input(handler):
    """Test message construction with no input message"""
    message = handler._construct_message(None)
    assert isinstance(message, str)
    assert message.count('|') == 2
    # Verify timestamp format
    parts = message.split('|')
    assert len(parts) == 3
    # Verify timestamp can be parsed
    timestamp = datetime.datetime.strptime(parts[1], "%Y-%m-%dT%H:%M:%SZ")
    assert isinstance(timestamp, datetime.datetime)

def test_construct_message_with_input(handler):
    """Test message construction with input message"""
    test_message = "test_message"
    message = handler._construct_message(test_message)
    assert message.startswith(test_message + "|")
    assert message.count('|') == 3

def test_construct_message_with_invalid_input(handler):
    """Test message construction with invalid input (contains |)"""
    with pytest.raises(ValueError) as exc_info:
        handler._construct_message("test|message")
    assert "message cannot contain | characters" in str(exc_info.value)

def test_add_serial_and_sign_message(handler, mock_chip):
    """Test adding serial number and signing message"""
    test_message = "test_message|123|2024-01-01T00:00:00Z"
    message, signature = handler._add_serial_and_sign_message(test_message, mock_chip)
    
    assert message.endswith(mock_chip.get_serial_number().hex())
    assert isinstance(signature, str)
    assert len(signature) == 128  # hex-encoded 64-byte signature
    mock_chip.get_signature.assert_called_once_with(message)

@patch('server.crypto.crypto.Chip')
def test_do_post_success(mock_chip_class, handler, mock_request_data, mock_chip):
    """Test successful POST request"""
    mock_chip_class.return_value.__enter__.return_value = mock_chip
    mock_request_data.data = {"message": "test_message"}
    
    status, response = handler.do_post(mock_request_data)
    
    assert status == 200
    response_data = json.loads(response)
    assert "message" in response_data
    assert "sign" in response_data
    assert len(response_data["sign"]) == 128
    assert response_data["message"].endswith(mock_chip.get_serial_number().hex())

@patch('server.crypto.crypto.Chip')
def test_do_post_invalid_message(mock_chip_class, handler, mock_request_data):
    """Test POST request with invalid message"""
    mock_request_data.data = {"message": "test|message"}
    
    status, response = handler.do_post(mock_request_data)
    
    assert status == 400
    response_data = json.loads(response)
    assert "status" in response_data
    assert "message cannot contain | characters" in response_data["status"]

@patch('server.crypto.crypto.Chip')
def test_do_post_no_message(mock_chip_class, handler, mock_request_data, mock_chip):
    """Test POST request with no message"""
    mock_chip_class.return_value.__enter__.return_value = mock_chip
    mock_request_data.data = {}
    
    status, response = handler.do_post(mock_request_data)
    
    assert status == 200
    response_data = json.loads(response)
    assert "message" in response_data
    assert "sign" in response_data