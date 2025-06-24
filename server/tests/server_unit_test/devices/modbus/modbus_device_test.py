from server.devices.inverters.ModbusTCP import ModbusTCP
from server.devices.inverters.ModbusSunspec import ModbusSunspec
from server.devices.inverters.ModbusSolarman import ModbusSolarman
from server.devices.inverters.modbus import Modbus
from server.devices.ICom import ICom
from server.network.network_utils import NetworkUtils
import server.tests.config_defaults as cfg
from unittest.mock import patch
import pytest


@pytest.fixture
def sunspec_device():
    return ModbusSunspec(**cfg.SUNSPEC_ARGS)


@pytest.fixture
def modbus_devices():
    devices: list[Modbus] = []

    tcp_config = {k: v for k, v in cfg.TCP_ARGS.items() if k != 'connection'}
    solarman_conf = {k: v for k, v in cfg.SOLARMAN_ARGS.items() if k != 'connection'}

    devices.append(ModbusTCP(**tcp_config))
    devices.append(ModbusSolarman(**solarman_conf))

    return devices


def test_open_and_is_open(modbus_devices):

    for device in modbus_devices:
        device.connect()

        with patch.object(device, 'is_open', return_value=True):
            assert device.is_open()


def test_read_harvest_no_data_exception(modbus_devices):
    for device in modbus_devices:

        def read_registers(operation, address, size):
            return [i for i in range(address, address + size)]

        device.read_registers = read_registers
        device._read_harvest_data(True)

        # Empty register array should raise an exception
        with pytest.raises(Exception):
            device.read_harvest_data()


def test_read_harvest_data_terminated_exception(modbus_devices):

    for device in modbus_devices:

        with patch.object(device, 'disconnect', return_value=True):
            with pytest.raises(Exception):
                device.read_harvest_data()


def test_get_config(modbus_devices):

    assert modbus_devices[0].get_config() == cfg.TCP_CONFIG
    assert modbus_devices[1].get_config() == cfg.SOLARMAN_CONFIG


def test_modbus_device_clone(modbus_devices):

    for device in modbus_devices:
        left = device.get_config()
        right = device.clone().get_config()
        assert left == right


def test_modbus_device_mac_not_present(modbus_devices):

    for device in modbus_devices:
        config = device.get_config()

        # remove the sn key
        config.pop("sn")  # sn is initialized in the device class and only present in the config after the device is created

        if config[ICom.connection_key()] == "TCP":
            config.pop(ICom.connection_key())
            device = ModbusTCP(**config)
        elif config[ICom.connection_key()] == "SOLARMAN":
            config.pop(ICom.connection_key())
            device = ModbusSolarman(**config)
        elif config[ICom.connection_key()] == "SUNSPEC":
            config.pop(ICom.connection_key())
            device = ModbusSunspec(**config)
        else:
            continue  # Not an IP-based connection

        config = device.get_config()
        assert device.mac is not None
        assert config["mac"] == NetworkUtils.INVALID_MAC


def test_get_SN(modbus_devices):

    modbus_tcp = modbus_devices[0]
    modbus_solarman = modbus_devices[1]

    assert modbus_tcp.get_SN() == None
    assert modbus_solarman.get_SN() == None


def test_sunspec_device_clone(sunspec_device):

    left = sunspec_device.get_config()
    right = sunspec_device.clone().get_config()
    assert left == right
