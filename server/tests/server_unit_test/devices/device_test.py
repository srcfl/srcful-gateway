import pytest
from unittest.mock import create_autospec, MagicMock
from server.devices.Device import Device
from server.devices.ICom import ICom, HarvestDataType, DER_TYPE
from typing import Optional

from server.network.network_utils import HostInfo

@pytest.fixture
def device():
    class TestDevice(Device):

        def __init__(self):
            super().__init__()
            self._is_connected = False
        
        def _connect(self, **kwargs) -> bool:
            self._is_connected = True
            return True
        
        def _disconnect(self) -> None:
            self._is_connected = False
        
        def _read_harvest_data(self, force_verbose) -> dict:
            return {"test": "data"}
        
        
        def is_valid(self) -> bool:
            return True

        def is_open(self) -> bool:
            return self._is_connected
        
        
        def get_harvest_data_type(self) -> HarvestDataType:
            return HarvestDataType.UNDEFINED
        
        def get_config(self) -> dict:
            return {"connection": "test"}
        
        def get_name(self) -> str:
            return "test"
        
        def clone(self, ip: Optional[str] = None) -> 'ICom':
            return TestDevice()
        
        def find_device(self) -> 'ICom':
            return TestDevice()
        
        def get_SN(self) -> str:
            return "qwe123"
        

        def compare_host(self, other: 'ICom') -> bool:
            return True

        def _clone_with_host(self, host: HostInfo) -> Optional[ICom]:
            return TestDevice()
        
        def _get_connection_type(self) -> str:
            return "test"
        
    
    return TestDevice()

def test_disconnect(device):
    assert not device.is_disconnected()
    device.disconnect()
    assert device.is_disconnected()

def test_disconnect_harvest_data(device):

    data = device.read_harvest_data(False)
    assert data is not None

    device.disconnect()

    with pytest.raises(Exception):
        device.read_harvest_data(False)

def test_connect(device):
    assert not device.is_open()
    device.connect()
    assert device.is_open()

    device.disconnect()
    assert not device.is_open()

    device.connect()
    assert not device.is_open()

def test_get_backoff_time_ms(device):
    assert device.get_backoff_time_ms(1000, 1000) == 2000
    
    assert device.get_backoff_time_ms(1000, 10000) == 9000

    assert device.get_backoff_time_ms(10, 10) == 1000

    assert device.get_backoff_time_ms(100000, 2560000) == 256000


