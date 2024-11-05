import pytest

from server.devices.inverters.ModbusSolarman import ModbusSolarman
from server.devices.inverters.ModbusTCP import ModbusTCP
from server.devices.inverters.modbus import Modbus
from server.network.network_utils import HostInfo
import server.tests.config_defaults as cfg


@pytest.fixture
def modbus_devices():
    devices: list[Modbus] = []
    
    tcp_config = {k: v for k, v in cfg.TCP_ARGS.items() if k != 'connection'}
    solarman_conf = {k: v for k, v in cfg.SOLARMAN_ARGS.items() if k != 'connection'}
    
    
    devices.append(ModbusTCP(**tcp_config))
    devices.append(ModbusSolarman(**solarman_conf))

    return devices

def test_clone_with_host(modbus_devices):
    for device in modbus_devices:
        host = HostInfo("1.2.3.4", "1234567890", device.mac)
        clone = device._clone_with_host(host)
        assert clone is not None
        assert clone.ip == "1.2.3.4"
        assert isinstance(clone, type(device))

def test_compare_host(modbus_devices):
    assert modbus_devices[0].compare_host(modbus_devices[1])

    modbus_devices[0].ip = "1.2.3.5"
    assert not modbus_devices[0].compare_host(modbus_devices[1])
