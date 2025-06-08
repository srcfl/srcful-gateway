from server.devices.inverters.ModbusTCP import ModbusTCP
import server.tests.config_defaults as cfg
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def modbus_tcp():
    return ModbusTCP(**cfg.TCP_CONFIG)


def test_ensure_sn_presists_when_cloning_devices_with_already_defined_sn(modbus_tcp):

    modbus_tcp.sn = 1234567890
    new_device = modbus_tcp.clone()

    # Create a mock client instance
    mock_client_instance = MagicMock()

    # Patch _create_client to do nothing, and set the client manually
    with patch.object(new_device, '_create_client', return_value=None) as mock_create_client, \
            patch('server.devices.inverters.ModbusTCP.NetworkUtils.get_mac_from_ip', return_value="00:11:22:33:44:55") as mock_get_mac:

        # Set the client attribute AFTER potentially preventing its creation
        new_device.client = mock_client_instance

        # Call _connect. Since new_device.sn should already be set, _read_SN should not be called.
        new_device._connect()

        # Assert that connect was called
        mock_client_instance.connect.assert_called_once()

        assert new_device.get_SN() == modbus_tcp.get_SN()
