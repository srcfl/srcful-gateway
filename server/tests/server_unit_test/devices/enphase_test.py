from server.devices.inverters.enphase import Enphase
from server.network.network_utils import HostInfo
from server.network.network_utils import NetworkUtils
import server.tests.config_defaults as cfg
import pytest
from unittest.mock import Mock

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

def test_disconnect(enphase):

    mock_session = Mock()
    enphase.session = mock_session
    
    enphase.disconnect()
    mock_session.close.assert_called_once()
    assert enphase.is_disconnected()
    assert not enphase.is_open()
