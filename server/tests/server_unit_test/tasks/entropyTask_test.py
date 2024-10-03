import pytest
from unittest.mock import Mock, patch, MagicMock
from server.tasks.entropyTask import EntropyTask, generate_poisson_delay, generate_entropy
from server.blackboard import BlackBoard
import server.crypto.crypto as crypto
import paho.mqtt.client as mqtt

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

@patch('server.crypto.crypto.Chip')
def test_generate_entropy(mock_chip):
    mock_chip_instance = Mock()
    mock_chip_instance.get_random.return_value = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08'
    mock_chip.return_value = mock_chip_instance

    entropy = generate_entropy(mock_chip_instance)
    assert isinstance(entropy, int)
    assert 0 <= entropy < 2**64

@patch('server.crypto.crypto.Chip')
def test_create_entropy_data(mock_chip, mock_blackboard):
    mock_chip_instance = Mock()
    mock_chip_instance.get_random.return_value = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08'
    mock_chip.return_value.__enter__.return_value = mock_chip_instance

    task = EntropyTask(0, mock_blackboard)
    entropy_data = task._create_entropy_data()

    assert isinstance(entropy_data, dict)
    assert 'entropy' in entropy_data
    assert isinstance(entropy_data['entropy'], int)
    assert 0 <= entropy_data['entropy'] < 2**64

@patch('paho.mqtt.client.Client')
def test_setup_mqtt(mock_mqtt_client, mock_blackboard):
    mock_ssl_context = MagicMock()
    with patch('ssl.create_default_context', return_value=mock_ssl_context):
        task = EntropyTask(0, mock_blackboard)
        task._setup_mqtt("cert_pem", "private_key", mock_blackboard.settings.entropy)

        mock_mqtt_client.assert_called_once()
        mock_mqtt_client.return_value.tls_set_context.assert_called_once_with(mock_ssl_context)
        mock_mqtt_client.return_value.connect.assert_called_once_with(
            mock_blackboard.settings.entropy.mqtt_broker,
            mock_blackboard.settings.entropy.mqtt_port
        )
        mock_mqtt_client.return_value.loop_start.assert_called_once()

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
def test_execute_when_mining(mock_send_entropy, mock_get_cert_and_key, mock_blackboard):
    mock_get_cert_and_key.return_value = ("cert_pem", "private_key")
    
    task = EntropyTask(0, mock_blackboard)
    result = task.execute(0)

    mock_get_cert_and_key.assert_called_once()
    mock_send_entropy.assert_called_once()
    assert result == task