import pytest
from unittest.mock import Mock, patch, MagicMock
from server.tasks.entropyTask import EntropyTask, generate_poisson_delay, generate_entropy, _LAST_INSTANCE_ID
from server.app.blackboard import BlackBoard
import server.crypto.crypto as crypto
import paho.mqtt.client as mqtt
import ssl
import tempfile
import os

@pytest.fixture
def mock_blackboard():
    bb = Mock(spec=BlackBoard)
    bb.settings = Mock()
    bb.settings.entropy = Mock()
    bb.settings.entropy.mqtt_broker = "test.mosquitto.org"
    bb.settings.entropy.mqtt_port = 8883
    bb.settings.entropy.mqtt_topic = "test/entropy"
    bb.settings.entropy.do_mine = True
    bb.time_ms.return_value = 1000
    return bb

def create_mock_chip_instance():
    mock_chip_instance = Mock()

    mock_chip_instance.get_random.return_value = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08'
    mock_chip_instance.get_serial.return_value = "1234567890"
    mock_chip_instance.sign_data.return_value = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08'

    return mock_chip_instance

@patch('server.crypto.crypto.Chip')
def test_generate_entropy(mock_chip):
    mock_chip_instance = create_mock_chip_instance()
    mock_chip.return_value = mock_chip_instance

    entropy = generate_entropy(mock_chip_instance)
    assert isinstance(entropy, int)
    assert 0 <= entropy < 2**64

@patch('server.crypto.crypto.Chip')
def test_create_entropy_data(mock_chip, mock_blackboard):
    mock_chip_instance = create_mock_chip_instance()
    mock_chip.return_value.__enter__.return_value = mock_chip_instance

    task = EntropyTask(0, mock_blackboard)
    entropy_data = task._create_entropy_data()

    assert isinstance(entropy_data, dict)
    assert 'entropy' in entropy_data
    assert isinstance(entropy_data['entropy'], int)
    assert 0 <= entropy_data['entropy'] < 2**64

@patch('paho.mqtt.client.Client')
def test_publish_entropy(mock_mqtt_client, mock_blackboard):
    task = EntropyTask(0, mock_blackboard)
    mqtt_client = mock_mqtt_client.return_value
    
    entropy_data = {"entropy": 12345}
    task._publish_entropy(mqtt_client, entropy_data, mock_blackboard.settings.entropy)

    mock_mqtt_client.return_value.publish.assert_called_once()
    args, _ = mock_mqtt_client.return_value.publish.call_args
    assert args[0] == mock_blackboard.settings.entropy.mqtt_topic
    assert '12345' in args[1]  # Check if the entropy value is in the payload

def test_execute_when_not_mining(mock_blackboard):
    mock_blackboard.settings.entropy.do_mine = False

    task = EntropyTask(0, mock_blackboard)
    result = task.execute(0)

    assert result is None

@patch.object(EntropyTask, '_get_cert_and_key')
@patch.object(EntropyTask, 'send_entropy')
@patch('server.crypto.crypto.Chip')
def test_execute_when_mining(mock_chip, mock_send_entropy, mock_get_cert_and_key, mock_blackboard):
    mock_chip_instance = create_mock_chip_instance()
    mock_chip.return_value.__enter__.return_value = mock_chip_instance


    mock_get_cert_and_key.return_value = ("cert_pem", "private_key")
    
    task = EntropyTask(0, mock_blackboard)
    result = task.execute(0)

    mock_get_cert_and_key.assert_called_once()
    mock_send_entropy.assert_called_once()
    assert result == task

def test_last_instance_id_increments(mock_blackboard):

    first_instance_id = _LAST_INSTANCE_ID
    task1 = EntropyTask(0, mock_blackboard)
    task2 = EntropyTask(0, mock_blackboard)
    task3 = EntropyTask(0, mock_blackboard)

    assert task2.instance_id == task1.instance_id + 1
    assert task3.instance_id == task2.instance_id + 1

@patch.object(EntropyTask, '_get_cert_and_key')
@patch.object(EntropyTask, 'send_entropy')
@patch('server.crypto.crypto.Chip')
def test_only_latest_instance_executes(mock_chip, mock_send_entropy, mock_get_cert_and_key, mock_blackboard):
    mock_chip_instance = create_mock_chip_instance()
    mock_chip.return_value.__enter__.return_value = mock_chip_instance

    mock_get_cert_and_key.return_value = ("cert_pem", "private_key")

    task1 = EntropyTask(0, mock_blackboard)
    task2 = EntropyTask(0, mock_blackboard)
    task3 = EntropyTask(0, mock_blackboard)

    result1 = task1.execute(0)
    result2 = task2.execute(0)
    result3 = task3.execute(0)

    assert result1 is None
    assert result2 is None
    assert result3 == task3

    mock_get_cert_and_key.assert_called_once()
    mock_send_entropy.assert_called_once()

@patch('logging.Logger.info')
@patch('server.crypto.crypto.Chip')
def test_non_latest_instance_logs_termination(mock_chip, mock_log_info, mock_blackboard):
    mock_chip_instance = create_mock_chip_instance()
    mock_chip.return_value.__enter__.return_value = mock_chip_instance

    task1 = EntropyTask(0, mock_blackboard)
    task2 = EntropyTask(0, mock_blackboard)

    task1.execute(0)

    mock_log_info.assert_called_once_with(
        f"Running version {task1.instance_id} is not the last instance id {task2.instance_id}, Terminating"
    )

@patch.object(EntropyTask, '_get_cert_and_key')
@patch.object(EntropyTask, 'send_entropy')
@patch('server.crypto.crypto.Chip') 
def test_latest_instance_executes_multiple_times(mock_chip, mock_send_entropy, mock_get_cert_and_key, mock_blackboard):
    mock_chip_instance = create_mock_chip_instance()
    mock_chip.return_value.__enter__.return_value = mock_chip_instance

    mock_get_cert_and_key.return_value = ("cert_pem", "private_key")

    task = EntropyTask(0, mock_blackboard)

    result1 = task.execute(0)
    result2 = task.execute(0)
    result3 = task.execute(0)

    assert result1 == task
    assert result2 == task
    assert result3 == task

    assert mock_get_cert_and_key.call_count == 1
    assert mock_send_entropy.call_count == 3