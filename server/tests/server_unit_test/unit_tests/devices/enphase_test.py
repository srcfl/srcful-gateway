from server.devices.inverters.enphase import Enphase
import server.tests.config_defaults as cfg
import pytest

@pytest.fixture
def enphase():
    return Enphase(**cfg.ENPHASE_CONFIG)


def test_open(enphase):
    assert not enphase.is_open()
