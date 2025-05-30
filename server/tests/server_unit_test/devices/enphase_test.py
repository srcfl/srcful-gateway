from requests import patch
import requests
from server.devices.inverters.enphase import Enphase
from server.network.network_utils import HostInfo
from server.network.network_utils import NetworkUtils
import server.tests.config_defaults as cfg
import pytest
from unittest.mock import Mock, patch
from server.network.mdns.mdns import ServiceResult


@pytest.fixture
def enphase():
    return Enphase(**cfg.ENPHASE_CONFIG)


@pytest.fixture
def config():
    return cfg.ENPHASE_CONFIG.copy()


def test_open(enphase):
    assert not enphase.is_open()


def test_clone(enphase):
    clone = enphase.clone()
    assert clone is not None
    assert clone.ip == enphase.ip
    assert clone.mac == enphase.mac
    assert clone.bearer_token == enphase.bearer_token


def test_clone_with_host(enphase):
    host = HostInfo(ip="192.168.1.100", port=80, mac=NetworkUtils.INVALID_MAC)
    clone = enphase._clone_with_host(host)
    assert clone is not None
    assert clone.ip != enphase.ip
    assert clone.port == enphase.port
    assert clone.mac == enphase.mac
    assert clone.bearer_token == enphase.bearer_token
    assert clone.get_name() == enphase.get_name()
    assert clone.get_SN() == enphase.get_SN()


def test_init_without_token_and_credentials(config):
    # remove the bearer token
    config.pop(Enphase.bearer_token_key())
    try:
        enphase = Enphase(**config)
        assert False
    except Exception as e:
        assert True


def test_init_with_credentials_and_no_token(config):
    config.pop(Enphase.bearer_token_key())
    config[Enphase.username_key()] = "test_user"
    config[Enphase.password_key()] = "test_password"
    config[Enphase.iq_gw_serial_key()] = "123qwe"
    enphase = Enphase(**config)
    assert not enphase.bearer_token
    assert enphase.iq_gw_serial == "123qwe"
    assert enphase.username == "test_user"
    assert enphase.password == "test_password"


def test_init_with_no_token_missing_username(config):
    config.pop(Enphase.bearer_token_key())
    config[Enphase.password_key()] = "test_password"
    config[Enphase.iq_gw_serial_key()] = "123qwe"
    try:
        enphase = Enphase(**config)
        assert False
    except Exception as e:
        assert True


def test_init_with_no_token_missing_password(config):
    config.pop(Enphase.bearer_token_key())
    config[Enphase.username_key()] = "test_user"
    config[Enphase.iq_gw_serial_key()] = "123qwe"
    try:
        enphase = Enphase(**config)
        assert False
    except Exception as e:
        assert True


def test_init_with_no_token_missing_iq_gw_serial(config):
    config.pop(Enphase.bearer_token_key())
    config[Enphase.username_key()] = "test_user"
    config[Enphase.password_key()] = "test_password"
    try:
        enphase = Enphase(**config)
        assert False
    except Exception as e:
        assert True


def test_is_open_disconnected():

    # with patch('server.devices.inverters.enphase.Enphase.NetworkUtils.get_mac_from_ip', return_value="1:1:1:1:1:1"):
    enphase = Enphase(**cfg.ENPHASE_CONFIG)

    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    enphase.make_get_request = Mock(return_value=mock_response)

    enphase._get_bearer_token = Mock(return_value="1234567890")
    enphase._read_SN = Mock(return_value="1234567890")

    NetworkUtils.get_mac_from_ip = Mock(return_value="1:1:1:1:1:1")

    assert enphase.connect()
    assert enphase.is_open()
    assert enphase.connect()
    assert enphase.is_open()
    enphase.disconnect()
    assert not enphase.is_open()


def test_disconnect(enphase):

    mock_session = Mock()
    enphase.session = mock_session

    enphase.disconnect()
    mock_session.close.assert_called_once()
    assert enphase.is_disconnected()
    assert not enphase.is_open()


def test_find_device_with_mdns():

    enphase = Enphase(**cfg.ENPHASE_CONFIG)

    mock_service_result = ServiceResult(
        name="envoy._enphase-envoy._tcp.local.",
        address="192.168.1.100",
        port=80,
        properties={"serialnum".encode(): "123456".encode()}
    )

    NetworkUtils.get_mac_from_ip = Mock(return_value="00:00:00:00:00:00")

    assert enphase.ip == "localhost"

    with patch('server.network.mdns.mdns.scan', return_value=[mock_service_result]):
        found_device = enphase.find_device()  # a new instance of Enphase with the new ip
        assert found_device is not None
        assert found_device.ip == "192.168.1.100"
        assert found_device.port == 80
        assert found_device.mac == enphase.mac
        assert found_device.bearer_token == enphase.bearer_token
