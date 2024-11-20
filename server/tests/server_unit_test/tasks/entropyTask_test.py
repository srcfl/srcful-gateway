import json
import time
import pytest
from unittest.mock import Mock, patch, MagicMock
from server.app.settings.settings import Settings
from server.app.settings.settings_observable import ChangeSource
from server.crypto.crypto_state import CryptoState
from server.tasks import entropy
from server.tasks.entropy.task import EntropyTask, generate_poisson_delay, generate_entropy, _LAST_INSTANCE_ID
from server.app.blackboard import BlackBoard
import server.crypto.crypto as crypto
import paho.mqtt.client as mqtt
import ssl
import tempfile
import os

@pytest.fixture
def mock_blackboard():
    bb = Mock(spec=BlackBoard)
    bb._crypto_state = Mock(spec=CryptoState)
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
    mock_chip_instance.get_serial_number.return_value = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01'
    mock_chip_instance.get_signature.return_value = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08'

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
    task._has_mined_srcful_data = Mock(return_value=True)
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
    task1._has_mined_srcful_data = Mock(return_value=True)
    task2 = EntropyTask(0, mock_blackboard)
    task2._has_mined_srcful_data = Mock(return_value=True)
    task3 = EntropyTask(0, mock_blackboard)
    task3._has_mined_srcful_data = Mock(return_value=True)

    result1 = task1.execute(0)
    result2 = task2.execute(0)
    result3 = task3.execute(0)

    assert result1 is None
    assert result2 is None
    assert result3 == task3

    mock_get_cert_and_key.assert_called_once()
    mock_send_entropy.assert_called_once()

def test_no_mined_srcful_data(mock_blackboard):
    task = EntropyTask(0, mock_blackboard)
    task._has_mined_srcful_data = Mock(return_value=False)
    task._send_entropy = Mock()
    result = task.execute(0)
    assert result == task
    assert task._send_entropy.call_count == 0
    assert task.get_time() == mock_blackboard.time_ms() + 60000
    

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

    task._has_mined_srcful_data = Mock(return_value=True)

    result1 = task.execute(0)
    result2 = task.execute(0)
    result3 = task.execute(0)

    assert result1 == task
    assert result2 == task
    assert result3 == task

    assert mock_get_cert_and_key.call_count == 1
    assert mock_send_entropy.call_count == 3


def test_create_entropy_data_with_software_crypto(mock_blackboard):
    ''' enable with software crypto'''
    with crypto.Chip() as chip:
        hardware_crypto = chip.is_hardware_crypto()

    if hardware_crypto:
        pytest.skip("Skipping test for hardware crypto")

    mock_blackboard.time_ms.return_value = int(time.time() * 1000)

    bb = BlackBoard(CryptoState())

    entropy_task = EntropyTask(0, bb)
    data = entropy_task._create_entropy_data()
    assert isinstance(data, dict)
    assert 'entropy' in data
    assert isinstance(data['entropy'], int)
    assert 0 <= data['entropy'] < 2**64
    assert isinstance(data['serial'], str)
    assert isinstance(data['sig'], str)
    assert isinstance(data['timestamp_sec'], int)
    json_data = json.dumps(data)
    assert len(json_data) > 0


def test_has_mined_srcful_data(mock_blackboard):

    # modify to use a gateway that has data if this fails.
    task = EntropyTask(0, mock_blackboard)
    mock_blackboard.settings.api.gql_endpoint = "https://api.srcful.dev"
    mock_blackboard.settings.api.gql_timeout = 10
    assert task._has_mined_srcful_data("0123b0e69662744eee")

def test_has_not_mined_srcful_data(mock_blackboard):
    task = EntropyTask(0, mock_blackboard)
    mock_blackboard.settings.api.gql_endpoint = "https://api.srcful.dev"
    mock_blackboard.settings.api.gql_timeout = 10
    assert not task._has_mined_srcful_data("f42ea576ac87184445")
    

def test_to_json_default_values():
    settings = Settings()
    json_str = settings.to_json()
    entropy_settings = entropy.EntropySettings()
    expected = {
        settings.entropy.DO_MINE: entropy_settings.do_mine,
        settings.entropy.MQTT_BROKER: entropy_settings.mqtt_broker,
        settings.entropy.MQTT_PORT: entropy_settings.mqtt_port,
        settings.entropy.MQTT_TOPIC: entropy_settings.mqtt_topic
    }

    for key, value in expected.items():
        assert json.loads(json_str)[settings.SETTINGS][settings.entropy.ENTROPY][key] == value

def test_to_json_custom_values():
    settings = Settings()
    entropy_settings = settings.entropy
    entropy_settings.set_do_mine(True, ChangeSource.LOCAL)
    entropy_settings.set_mqtt_broker("broker", ChangeSource.LOCAL)
    entropy_settings.set_mqtt_port(1717, ChangeSource.LOCAL)
    entropy_settings.set_mqtt_topic("topic", ChangeSource.LOCAL)
    json_str = settings.to_json()
    expected = {
                settings.entropy.DO_MINE: entropy_settings.do_mine,
                settings.entropy.MQTT_BROKER: entropy_settings.mqtt_broker,
                settings.entropy.MQTT_PORT: entropy_settings.mqtt_port,
                settings.entropy.MQTT_TOPIC: entropy_settings.mqtt_topic
    }

    for key, value in expected.items():
        assert json.loads(json_str)[settings.SETTINGS][entropy.EntropySettings.ENTROPY][key] == value
        

def test_from_json_custom_values():
    settings = Settings()
    expected_settings = entropy.EntropySettings()
    expected_settings.set_do_mine(True, ChangeSource.LOCAL)
    expected_settings.set_mqtt_broker("broker", ChangeSource.LOCAL)
    expected_settings.set_mqtt_port(1717, ChangeSource.LOCAL)
    expected_settings.set_mqtt_topic("topic", ChangeSource.LOCAL)

    settings_dict = { settings.SETTINGS: { entropy.EntropySettings.ENTROPY: expected_settings.to_dict() } }

    settings.from_json(json.dumps(settings_dict), ChangeSource.LOCAL)

    assert settings.entropy.do_mine == expected_settings.do_mine
    assert settings.entropy.mqtt_broker == expected_settings.mqtt_broker
    assert settings.entropy.mqtt_port == expected_settings.mqtt_port
    assert settings.entropy.mqtt_topic == expected_settings.mqtt_topic

# {'entropy': 9380403298322624419, 'serial': 'f42ea576ac87184445', 'sig': '91628a5e0db092ebb1b94b0049cf0403fa13baccf1590a9ae331679a4fb4b49b86db7417644cb70469f673bbf378f313a531f4892ee4b2a86f623accb8a5622a', 'timestamp_sec': 1731935173}