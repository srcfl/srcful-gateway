import pytest
import json
from server.web.handler.delete.notification import Handler  # Replace with actual module import path


# Assuming Message class has a constructor accepting these parameters
@pytest.fixture
def mock_request_data():
    class MockRequestData:
        def __init__(self):
            self.post_params = {}
            self.bb = MockBB()

    class MockBB:
        def delete_message(self, message_id: int):
            # Simulate delete operation; return True if message exists, else False
            existing_ids = {1, 2, 3}  # Preset message IDs for testing
            return message_id in existing_ids

    return MockRequestData()


# Testing Handler.delete success case
def test_handler_delete_success(mock_request_data):
    handler = Handler()
    test_id = '2'  # Assuming this ID exists
    mock_request_data.post_params['id'] = test_id

    status_code, response = handler.do_delete(mock_request_data)
    response_data = json.loads(response)

    assert status_code == 200
    assert response_data == {"id": str(test_id)}
    

# Testing Handler.delete not found case
def test_handler_delete_not_found(mock_request_data):
    handler = Handler()
    test_id = '99'  # Assuming this ID does not exist
    mock_request_data.post_params['id'] = test_id

    status_code, response = handler.do_delete(mock_request_data)
    response_data = json.loads(response)

    assert status_code == 404
    assert response_data == {"id": str(test_id)}
