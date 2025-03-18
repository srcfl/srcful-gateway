import server.tasks.srcfulAPICallTask as apiCall
from unittest.mock import Mock, patch
import requests


class ConcreteSUT(apiCall.SrcfulAPICallTask):
    def __init__(self, event_time: int, bb):
        super().__init__(event_time, bb)
        self.post_url = "https://testnet.srcful.dev/gw/data/"

    def _on_200(self, reply: requests.Response):
        return None

    def _on_error(self, reply: requests.Response):
        return None


def test_createSrcfulAPICall():
    t = ConcreteSUT(0, {})
    assert t is not None


def test_execute_calls_post_and_handles_200_response():
    mock_data = {"foo": "bar"}
    mock_response = Mock()
    mock_response.status_code = 200
    mock_on200 = Mock()
    task = ConcreteSUT(0, {})

    # Mock the requests module so we can intercept the post() call
    with patch("requests.post") as mock_post:
        mock_post.return_value = mock_response
        task._data = Mock(return_value=mock_data)
        task._on_200 = mock_on200

        task.execute(0)

        # wait for the thread to finish
        mock_post.assert_called_once_with(
            "https://testnet.srcful.dev/gw/data/", data=mock_data, timeout=5
        )

        mock_on200.assert_called_once_with(mock_response)


def test_execute_calls_post_and_handles_post_request_exception():
    # should answer with an empty response
    mock_data = {"foo": "bar"}
    mock_response = requests.Response()
    mock_on_error = Mock(return_value=0)
    task = ConcreteSUT(0, {})

    # Mock the requests module so we can intercept the post() call
    with patch(
        "requests.post", side_effect=requests.exceptions.RequestException
    ) as mock_post:
        mock_post.return_value = mock_response
        task._data = Mock(return_value=mock_data)
        task._on_error = mock_on_error

        task.execute(0)

        # wait for the thread to finish
        mock_post.assert_called_once_with(
            "https://testnet.srcful.dev/gw/data/", data=mock_data, timeout=5
        )

        # check that onError was called with a requests.Response object
        assert mock_on_error.call_args[0][0].status_code == None

        mock_on_error.assert_called_once()


def test_execute_calls_post_and_handles_non_200_response():
    mock_data = {"foo": "bar"}
    mock_response = Mock()
    mock_response.status_code = 500
    mock_on_error = Mock(return_value=(1000))
    task = ConcreteSUT(0, {})

    # Mock the requests module so we can intercept the post() call
    with patch("requests.post") as mock_post:
        mock_post.return_value = mock_response
        task._data = Mock(return_value=mock_data)
        task._on_error = mock_on_error

        result = task.execute(0)
        mock_post.assert_called_once_with(
            "https://testnet.srcful.dev/gw/data/", data=mock_data, timeout=5
        )

        mock_on_error.assert_called_once_with(mock_response)

        assert result.time == 1000

def test_execute_calls_post_and_handles_non_200_response_with_tasks():
    mock_data = {"foo": "bar"}
    mock_response = Mock()
    mock_response.status_code = 500
    mock_on_error = Mock(return_value=(1000, Mock()))
    task = ConcreteSUT(0, {})

    # Mock the requests module so we can intercept the post() call
    with patch("requests.post") as mock_post:
        mock_post.return_value = mock_response
        task._data = Mock(return_value=mock_data)
        task._on_error = mock_on_error

        result = task.execute(0)
        mock_post.assert_called_once_with(
            "https://testnet.srcful.dev/gw/data/", data=mock_data, timeout=5
        )

        mock_on_error.assert_called_once_with(mock_response)

        # Assert that the result is a list containing the task and the mock
        assert isinstance(result, list)
        assert len(result) == 2
        mock_index = next(i for i, item in enumerate(result) if isinstance(item, Mock))
        task_index = next(i for i, item in enumerate(result) if isinstance(item, ConcreteSUT))
        assert mock_index != task_index
        assert isinstance(result[mock_index], Mock)
        assert result[task_index] == task



def test_execute_handles_request_exception_returns_time():
    # Arrange
    mock_data = {"foo": "bar"}
    mock_on_error = Mock(return_value=1000)
    task = ConcreteSUT(0, {})

    # Mock the requests module so it raises a RequestException when post() is called
    with patch("requests.post", side_effect=requests.exceptions.RequestException):
        # Set the task's _data method to return our mock data
        task._data = Mock(return_value=mock_data)

        # Set the task's _onError method to our mock method
        task._on_error = mock_on_error

        # Act
        result = task.execute(0)

        # Assert
        mock_on_error.assert_called_once()
        assert result == task
        assert result.reply.status_code == None
        assert result.time == 1000

def test_execute_handles_request_exception_returns_task():
    # Arrange
    mock_data = {"foo": "bar"}
    return_task = ConcreteSUT(0, {})
    mock_on_error = Mock(return_value=return_task)
    task = ConcreteSUT(0, {})

    # Mock the requests module so it raises a RequestException when post() is called
    with patch("requests.post", side_effect=requests.exceptions.RequestException):
        # Set the task's _data method to return our mock data
        task._data = Mock(return_value=mock_data)

        # Set the task's _onError method to our mock method
        task._on_error = mock_on_error

        # Act
        result = task.execute(0)

        # Assert
        mock_on_error.assert_called_once()
        assert task.reply.status_code == None
        assert return_task in result

def test_execute_handles_request_exception_returns_time_and_task():
    # Arrange
    mock_data = {"foo": "bar"}
    return_task = ConcreteSUT(0, {})
    mock_on_error = Mock(return_value=(1000, return_task))
    task = ConcreteSUT(0, {})

    # Mock the requests module so it raises a RequestException when post() is called
    with patch("requests.post", side_effect=requests.exceptions.RequestException):
        # Set the task's _data method to return our mock data
        task._data = Mock(return_value=mock_data)

        # Set the task's _onError method to our mock method
        task._on_error = mock_on_error

        # Act
        result = task.execute(0)

        # Assert
        mock_on_error.assert_called_once()
        assert task.reply.status_code == None
        assert return_task in result
        assert task in result

def test_handle_error_returns_none_if_no_error():
    task = ConcreteSUT(0, {})
    task._on_error = Mock(return_value=None)
    assert ConcreteSUT(0, {})._handle_error(None, 0) is None

def test_handle_error_returns_task_time():
    task = ConcreteSUT(0, {})
    task._on_error = Mock(return_value=1000)
    assert task._handle_error(None, 0) == task

def test_handle_error_returns_time_and_task():
    task = ConcreteSUT(0, {})
    task2 = ConcreteSUT(0, {})
    task.adjust_time(1)
    task2.adjust_time(2)
    task._on_error = Mock(return_value=(1000, task2))
    ret = task._handle_error(None, 1)
    assert task in ret
    assert task2 in ret
    assert task.time == 1001

def test_handle_error_returns_tasks():
    task = ConcreteSUT(0, {})
    task2 = ConcreteSUT(0, {})
    task3 = ConcreteSUT(0, {})

    # we need to set times as this is used in equals tests
    task.adjust_time(1)
    task2.adjust_time(2)
    task3.adjust_time(3)

    task._on_error = Mock(return_value=[task2, task3])
    ret = task._handle_error(None, 0)
    assert task not in ret
    assert task2 in ret
    assert task3 in ret
    assert task.time == 1

def test_execute_handles_exception():
    # Arrange
    mock_data = {"foo": "bar"}
    mock_on_error = Mock(return_value=1000)
    task = ConcreteSUT(0, {})

    # Set the task's _data method to return our mock data
    task._data = Mock(return_value=mock_data, side_effect=Exception("test"))

    # Set the task's _onError method to our mock method
    task._on_error = mock_on_error

    # Act
    res = task.execute(0)

    # Assert
    assert res == task
    mock_on_error.assert_called_once()
    assert task.reply.status_code == None
    assert task.time == 1000


def test_json_returns_none_by_default():
    assert ConcreteSUT(0, {})._json() is None


def test_data_returns_none_by_default():
    assert ConcreteSUT(0, {})._data() is None
