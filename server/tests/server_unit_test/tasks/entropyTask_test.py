import pytest
from unittest.mock import Mock, patch
from server.tasks.entropyTask import EntropyTask, generate_poisson_delay, generate_entropy
from server.blackboard import BlackBoard
import server.crypto.crypto as crypto
import requests

@pytest.fixture
def mock_blackboard():
    bb = Mock(spec=BlackBoard)
    bb.entropy = Mock()
    bb.entropy.endpoint = "http://test-endpoint.com"
    bb.entropy.do_mine = True
    return bb

def test_generate_poisson_delay():
    delay = generate_poisson_delay()
    assert isinstance(delay, int)
    assert delay > 0

def test_generate_entropy():
    for _ in range(100):
        entropy = generate_entropy()
        assert isinstance(entropy, int)
        assert 0 <= entropy < 2**64 # checks that we are generating a random 64 bit integer

@patch('server.crypto.crypto.Chip')
def test_create_jwt_success(mock_chip, mock_blackboard):
    mock_chip_instance = Mock()
    mock_chip_instance.get_serial_number.return_value = b'1234'
    mock_chip_instance.build_jwt.return_value = "test_jwt"
    mock_chip.return_value.__enter__.return_value = mock_chip_instance

    task = EntropyTask(0, mock_blackboard)
    jwt = task._create_jwt()

    assert jwt == "test_jwt"
    mock_chip_instance.build_jwt.assert_called_once()


@patch('server.tasks.entropyTask.EntropyTask._create_jwt')
@patch('server.tasks.srcfulAPICallTask.SrcfulAPICallTask.execute')
def test_execute_when_mining(mock_execute, mock_create_jwt, mock_blackboard):
    mock_create_jwt.return_value = "test_jwt"
    mock_execute.return_value = "test_response"

    task = EntropyTask(0, mock_blackboard)
    result = task.execute(0)

    assert result == "test_response"
    mock_execute.assert_called_once()

@patch('server.tasks.srcfulAPICallTask.SrcfulAPICallTask.execute')
def test_execure_when_not_mining(mock_execute, mock_blackboard):
    mock_blackboard.entropy.do_mine = False

    task = EntropyTask(0, mock_blackboard)
    result = task.execute(0)

    assert result is None
    mock_execute.assert_not_called()

@patch('server.tasks.entropyTask.EntropyTask._create_jwt')
@patch('server.crypto.revive_run.as_process')
def test_data_with_retries(mock_revive, mock_create_jwt, mock_blackboard):
    mock_create_jwt.side_effect = [
        crypto.Chip.Error(1, "Test error"),
        crypto.Chip.Error(1, "Test error"),
        "test_jwt"
    ]

    task = EntropyTask(0, mock_blackboard)
    result = task._data()

    assert result == "test_jwt"
    assert mock_create_jwt.call_count == 3
    assert mock_revive.call_count == 2

@patch('server.tasks.entropyTask.EntropyTask._create_jwt')
@patch('server.crypto.revive_run.as_process')
def test_data_max_retries_reached(mock_revive, mock_create_jwt, mock_blackboard):
    mock_create_jwt.side_effect = crypto.Chip.Error(1, "Test error")

    task = EntropyTask(0, mock_blackboard)
    with pytest.raises(crypto.Chip.Error):
        task._data()

    assert mock_create_jwt.call_count == 5
    assert mock_revive.call_count == 5
    mock_blackboard.increment_chip_death_count.assert_called_once()

@patch('server.tasks.entropyTask.generate_poisson_delay')
def test_on_200(mock_generate_delay, mock_blackboard):
    mock_generate_delay.return_value = 1000
    mock_blackboard.time_ms.return_value = 0

    task = EntropyTask(0, mock_blackboard)
    result = task._on_200("test_reply")

    assert isinstance(result, EntropyTask)
    assert task.get_time() == 1000

def test_on_error(mock_blackboard):
    mock_response = Mock(spec=requests.Response)
    mock_response.text = "Error message"

    task = EntropyTask(0, mock_blackboard)
    result = task._on_error(mock_response)

    assert result == 0
