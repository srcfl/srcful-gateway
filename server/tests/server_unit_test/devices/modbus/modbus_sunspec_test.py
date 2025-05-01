from server.devices.inverters.ModbusSunspec import ModbusSunspec
import server.tests.config_defaults as cfg
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def modbus_sunspec():
    return ModbusSunspec(**cfg.SUNSPEC_CONFIG)


def test_ensure_sn_presists_when_cloning_devices_with_already_defined_sn(modbus_sunspec):

    modbus_sunspec.sn = 1234567890
    new_device = modbus_sunspec.clone()

    with patch('server.devices.inverters.ModbusSunspec.client.SunSpecModbusClientDeviceTCP') as MockClientClass:

        # Setup the client attribute AFTER potentially preventing its creation
        mock_client_instance = MockClientClass.return_value

        # We need at least one model for the _connect method to not return False before the SN check
        mock_client_instance.models = {'common': MagicMock()}

        # Call _connect. Since new_device.sn should already be set, _read_SN should not be called.
        new_device._connect()

        assert new_device.get_SN() == modbus_sunspec.get_SN()
