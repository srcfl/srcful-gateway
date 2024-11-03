from server.devices.inverters.enphase import Enphase
from server.network.network_utils import HostInfo
from server.network.network_utils import NetworkUtils
import server.tests.config_defaults as cfg
import pytest

@pytest.fixture
def enphase():
    return Enphase(**cfg.ENPHASE_CONFIG)

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