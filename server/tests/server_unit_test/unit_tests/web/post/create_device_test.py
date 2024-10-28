import pytest
from unittest.mock import MagicMock
import server.tests.config_defaults as cfg
from server.web.handler.post.device import Handler as DeviceHandler

@pytest.fixture
def device_config():
    data = MagicMock()
    data.data = cfg.TCP_ARGS
    return data

@pytest.fixture
def handler():
    return DeviceHandler()

def test_create_device(device_config, handler):
    response = handler.do_post(device_config)
    
    assert response[0] == 200
    
    
