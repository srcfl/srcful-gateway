import pytest
from unittest.mock import Mock, patch
import json
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
from server.tasks.requestResponseTask import RequestTask, ResponseTask, handle_request, handle_request_task
from server.web import handler


@pytest.fixture
def mock_handler():
    return Mock(spec=handler.Handler)


@pytest.fixture
def mock_request_data():
    return Mock(spec=handler.RequestData)


def test_request_task_execute(blackboard, mock_handler, mock_request_data):
    request_task = RequestTask(1000, blackboard, 17, mock_handler, mock_request_data)

    # Set up the mock handler to return a success response
    mock_handler.do.return_value = (200, "Success")

    result = request_task.execute(1500)

    assert isinstance(result, ResponseTask)
    assert result.data["id"] == 17
    assert result.data["code"] == 200
    assert result.data["response"] == "Success"

    # Verify that the handler methods was called
    assert mock_handler.do.called


@patch('server.tasks.requestResponseTask.crypto.Chip')
def test_response_task_execute(mock_chip, blackboard):
    mock_chip_instance = Mock()
    mock_chip_instance.get_serial_number.return_value = b'1234'
    mock_chip_instance.get_signature.return_value = b'signature'
    mock_chip.return_value.__enter__.return_value = mock_chip_instance

    response_task = ResponseTask(1000, blackboard, 17, {"data": "test_data"})

    with patch('server.tasks.srcfulAPICallTask.SrcfulAPICallTask.execute') as mock_execute:
        response_task.execute(1500)
        mock_execute.assert_called_once()


def test_handle_request_valid(blackboard):
    request_data = {
        'method': 'GET',
        'path': '/api/test',
        'headers': {},
        'body': {},
        'query': {},
        'timestamp': blackboard.time_ms() // 1000,
        'id': 'test_id'
    }

    with patch('server.tasks.requestResponseTask.Endpoints') as mock_entitites:
        mock_endpoints = Mock()
        mock_endpoints.pre_do.return_value = ('/api/test', {})
        mock_endpoints.get_api_handler.return_value = (Mock(), {})
        mock_entitites.return_value = mock_endpoints

        result = handle_request(blackboard, request_data)

    assert isinstance(result, RequestTask)
    assert result.id == 'test_id'


def test_handle_request_invalid_method(blackboard):
    request_data = {
        'method': 'INVALID',
        'path': '/api/test',
        'headers': {},
        'body': {},
        'query': {},
        'timestamp': blackboard.time_ms() // 1000,
        'id': 17
    }

    result = handle_request(blackboard, request_data)

    assert isinstance(result, ResponseTask)
    assert result.data['error'] == "Method INVALID not allowed"


def test_handle_request_old_timestamp(blackboard):
    request_data = {
        'method': 'GET',
        'path': '/api/test',
        'headers': {},
        'body': {},
        'query': {},
        'timestamp': 0,
        'id': 'test_id'
    }

    result = handle_request(blackboard, request_data)

    assert isinstance(result, ResponseTask)
    assert "Request too old" in result.data['error']


def test_handle_request_task(blackboard):
    request_data = {
        'method': 'GET',
        'path': '/api/test',
        'headers': {},
        'body': {},
        'query': {},
        'timestamp': blackboard.time_ms() // 1000,
        'id': 'test_id'
    }

    data = {
        'subKey': RequestTask.SUBKEY,
        'data': json.dumps(request_data)
    }

    with patch('server.tasks.requestResponseTask.handle_request') as mock_handle_request:
        handle_request_task(blackboard, data)
        mock_handle_request.assert_called_once_with(blackboard, request_data)


def test_handle_request_task_wrong_subkey(blackboard):
    data = {
        'subKey': 'wrong_subkey',
        'data': '{}'
    }

    result = handle_request_task(blackboard, data)

    assert result is None

# test when the api handler is not found


def test_handle_request_task_api_handler_not_found(blackboard):

    nonexistent_path = '/api/nonexistent'

    data = {
        'subKey': RequestTask.SUBKEY,
        'data': json.dumps({
            'method': 'GET',
            'path': nonexistent_path,
            'headers': {},
            'body': {},
            'query': {},
            'timestamp': blackboard.time_ms() // 1000,
            'id': 'test_id'
        })
    }

    result = handle_request_task(blackboard, data)
    assert isinstance(result, ResponseTask)
    assert result.data['error'] == f"API handler not found for path {nonexistent_path}"
