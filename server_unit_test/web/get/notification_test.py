import json
import pytest
from server.web.handler.get.notification import ListHandler, MessageHandler
from server.message import Message 
from server.blackboard import BlackBoard

# Assuming Message class has a constructor accepting these parameters
@pytest.fixture
def mock_messages():
    return [
        Message("Error message 1", Message.Type.Error, 1617890123, 1),
        Message("Warning message 2", Message.Type.Warning, 1617890124, 2),
        Message("Info message 3", Message.Type.Info, 1617890125, 3),
    ]

@pytest.fixture
def mock_request_data(mock_messages):
    class MockRequestData:
        def __init__(self, messages):
            self.parameters = {}
            self.bb = BlackBoard()
            
            messages[0] = self.bb.add_error(messages[0].message)
            messages[1] = self.bb.add_warning(messages[1].message)
            messages[2] = self.bb.add_info(messages[2].message)

    return MockRequestData(mock_messages)

# Testing ListHandler
def test_list_handler_success(mock_request_data):
    list_handler = ListHandler()
    expected_ids = [m.id for m in mock_request_data.bb.messages]

    status_code, response = list_handler.do_get(mock_request_data)
    response_data = json.loads(response)

    assert status_code == 200
    assert "ids" in response_data
    assert response_data["ids"] == expected_ids

# Testing MessageHandler success case
def test_message_handler_success(mock_request_data):
    message_handler = MessageHandler()
    test_id = mock_request_data.bb.messages[0].id
    mock_request_data.parameters['id'] = test_id
    
    expected_message = next(m for m in mock_request_data.bb.messages if m.id == test_id)

    status_code, response = message_handler.do_get(mock_request_data)
    response_data = json.loads(response)

    assert status_code == 200
    assert response_data == {
        "message": expected_message.message,
        "type": expected_message.type.value,
        "timestamp": expected_message.timestamp,
        "id": expected_message.id,
    }

# Testing MessageHandler not found case
def test_message_handler_not_found(mock_request_data):
    message_handler = MessageHandler()
    test_id = 99  # Assuming this ID does not exist in mock_messages
    mock_request_data.parameters['id'] = test_id

    status_code, response = message_handler.do_get(mock_request_data)
    response_data = json.loads(response)

    assert status_code == 404
    assert response_data == {"message": f"message {test_id} not found"}
