import pytest
from unittest.mock import Mock, patch
from server.tasks.entrophyTask import EntrophyTask, generate_poisson_delay, generate_entropy
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

    task = EntrophyTask(0, mock_blackboard)
    jwt = task._create_jwt()

    assert jwt == "test_jwt"
    mock_chip_instance.build_jwt.assert_called_once()

@patch('server.crypto.crypto.Chip')
def test_create_jwt_error(mock_chip, mock_blackboard):
    mock_chip_instance = Mock()
    mock_chip_instance.build_jwt.side_effect = crypto.Chip.Error("Test error")
    mock_chip.return_value.__enter__.return_value = mock_chip_instance

    task = EntrophyTask(0, mock_blackboard)
    with pytest.raises(crypto.Chip.Error):
        task._create_jwt()

@patch('server.tasks.entrophyTask.EntrophyTask._create_jwt')
@patch('server.tasks.srcfulAPICallTask.SrcfulAPICallTask.post_data')
def test_post_data_when_mining(mock_post_data, mock_create_jwt, mock_blackboard):
    mock_create_jwt.return_value = "test_jwt"
    mock_post_data.return_value = "test_response"

    task = EntrophyTask(0, mock_blackboard)
    result = task.post_data()

    assert result == "test_response"
    mock_post_data.assert_called_once()

@patch('server.tasks.srcfulAPICallTask.SrcfulAPICallTask.post_data')
def test_post_data_when_not_mining(mock_post_data, mock_blackboard):
    mock_blackboard.entropy.do_mine = False

    task = EntrophyTask(0, mock_blackboard)
    result = task.post_data()

    assert result is None
    mock_post_data.assert_not_called()

@patch('server.tasks.entrophyTask.EntrophyTask._create_jwt')
@patch('server.crypto.revive_run.as_process')
def test_data_with_retries(mock_revive, mock_create_jwt, mock_blackboard):
    mock_create_jwt.side_effect = [
        crypto.Chip.Error("Test error"),
        crypto.Chip.Error("Test error"),
        "test_jwt"
    ]

    task = EntrophyTask(0, mock_blackboard)
    result = task._data()

    assert result == "test_jwt"
    assert mock_create_jwt.call_count == 3
    assert mock_revive.call_count == 2

@patch('server.tasks.entrophyTask.EntrophyTask._create_jwt')
@patch('server.crypto.revive_run.as_process')
def test_data_max_retries_reached(mock_revive, mock_create_jwt, mock_blackboard):
    mock_create_jwt.side_effect = crypto.Chip.Error("Test error")

    task = EntrophyTask(0, mock_blackboard)
    with pytest.raises(crypto.Chip.Error):
        task._data()

    assert mock_create_jwt.call_count == 5
    assert mock_revive.call_count == 4
    mock_blackboard.increment_chip_death_count.assert_called_once()

@patch('server.tasks.entrophyTask.generate_poisson_delay')
def test_on_200(mock_generate_delay, mock_blackboard):
    mock_generate_delay.return_value = 1000
    mock_blackboard.get_time.return_value = 0

    task = EntrophyTask(0, mock_blackboard)
    result = task._on_200("test_reply")

    assert isinstance(result, EntrophyTask)
    assert task.event_time == 1000

def test_on_error(mock_blackboard):
    mock_response = Mock(spec=requests.Response)
    mock_response.text = "Error message"

    task = EntrophyTask(0, mock_blackboard)
    result = task._on_error(mock_response)

    assert result == 0
