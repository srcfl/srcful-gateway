from server.devices.inverters.ModbusSolarman import ModbusSolarman
import server.tests.config_defaults as cfg
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def modbus_solarman():
    return ModbusSolarman(**cfg.SOLARMAN_CONFIG)


def test_ensure_sn_presists_when_cloning_devices_with_already_defined_sn(modbus_solarman):

    modbus_solarman.sn = 1234567890
    new_device = modbus_solarman.clone()

    # Create a mock client instance
    mock_client_instance = MagicMock()
    # The _connect method checks the 'sock' attribute
    # mock_client_instance.sock = True

    with patch.object(new_device, '_create_client', return_value=None) as mock_create_client, \
            patch('server.devices.inverters.ModbusSolarman.NetworkUtils.get_mac_from_ip', return_value="00:11:22:33:44:55") as mock_get_mac:

        # Set the client attribute AFTER potentially preventing its creation
        new_device.client = mock_client_instance

        # Call _connect. Since new_device.sn should already be set, _read_SN should not be called.
        new_device._connect()

        assert new_device.get_SN() == modbus_solarman.get_SN()
