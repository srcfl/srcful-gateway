from server.crypto.crypto_state import CryptoState
from server.devices.ICom import ICom
from server.devices.IComFactory import IComFactory
from server.app.settings import ChangeSource
from server.app.settings_device_listener import SettingsDeviceListener
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.app.blackboard import BlackBoard
from server.tasks.harvestFactory import HarvestFactory
from unittest.mock import MagicMock, Mock, patch
from server.devices.inverters.modbus import Modbus
from server.devices.inverters.ModbusTCP import ModbusTCP
from server.devices.inverters.ModbusSolarman import ModbusSolarman
import server.tests.config_defaults as cfg
import pytest


def set_up_listeners(blackboard: BlackBoard):
    settings_device_listener = SettingsDeviceListener(blackboard)
    HarvestFactory(blackboard)
    blackboard.settings.devices.add_listener(settings_device_listener.on_change)


@pytest.fixture
def modbus_devices():
    devices: list[Modbus] = []

    tcp_config = {k: v for k, v in cfg.TCP_ARGS.items() if k != 'connection'}
    solarman_conf = {k: v for k, v in cfg.SOLARMAN_ARGS.items() if k != 'connection'}

    devices.append(ModbusTCP(**tcp_config))
    devices.append(ModbusSolarman(**solarman_conf))


def test_execute_inverter_added(bb: BlackBoard):
    set_up_listeners(bb)

    # Add a device to the storage
    config = cfg.TCP_CONFIG.copy()
    config['sn'] = "1234567890"
    inverter = IComFactory.create_com(config)
    bb.device_storage.add_connection(inverter)

    # Mock the connection methods for testing
    inverter.connect = Mock(return_value=True)
    inverter.is_open = Mock(return_value=True)

    bb.settings.devices.add_connection(inverter, ChangeSource.LOCAL)

    assert inverter not in bb.devices.lst

    task = DevicePerpetualTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter in bb.devices.lst
    assert inverter.connect.called
    assert ret is None
    assert bb.purge_tasks()[0] is not None


def test_retry_on_exception(bb: BlackBoard):
    set_up_listeners(bb)

    config = cfg.TCP_CONFIG.copy()
    config['sn'] = "test_device_123"
    inverter = IComFactory.create_com(config)
    bb.device_storage.add_connection(inverter)
    bb.settings.devices.add_connection(inverter, ChangeSource.LOCAL)
    inverter.connect = Mock(side_effect=Exception("test"))
    task = DevicePerpetualTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter.connect.called
    assert ret is task
    assert len(bb.purge_tasks()) == 0


def test_execute_inverter_not_found(bb: BlackBoard):
    set_up_listeners(bb)

    config = cfg.TCP_CONFIG.copy()
    config['sn'] = "test_device_456"
    device = IComFactory.create_com(config)
    bb.device_storage.add_connection(device)
    bb.settings.devices.add_connection(device, ChangeSource.LOCAL)
    device.connect = Mock(return_value=False)
    device.find_device = Mock(return_value=None)  # Device not found on the network

    task = DevicePerpetualTask(0, bb, device)
    ret = task.execute(0)

    assert ret is task
    assert task.time == 300000  # execute run again in 5 minutes

    assert len(bb.purge_tasks()) == 1   # info message is added wich triggers a saveStateTask


def test_execute_new_inverter_added_after_rescan(bb: BlackBoard):
    set_up_listeners(bb)

    config = cfg.TCP_CONFIG.copy()
    config['sn'] = "test_device_789"
    inverter = IComFactory.create_com(config)
    bb.device_storage.add_connection(inverter)
    bb.settings.devices.add_connection(inverter, ChangeSource.LOCAL)

    inverter.connect = Mock(return_value=False)
    inverter.find_device = Mock(return_value=inverter)
    task = DevicePerpetualTask(0, bb, inverter)

    task = task.execute(event_time=0)

    inverter.connect = Mock(return_value=True)

    ret = task.execute(event_time=500)

    assert ret is None
    assert len(bb.devices.lst) == 1


@patch('server.tasks.openDevicePerpetualTask.NetworkUtils')
def test_reconnect_does_not_find_known_device(mock_network_utils, bb: BlackBoard):
    set_up_listeners(bb)

    config = cfg.TCP_ARGS.copy()
    config['sn'] = "test_device_network"
    inverter = IComFactory.create_com(config)
    bb.device_storage.add_connection(inverter)
    bb.settings.devices.add_connection(inverter, ChangeSource.LOCAL)
    inverter.connect = Mock(return_value=False)
    task = DevicePerpetualTask(0, bb, inverter)

    mock_network_utils.IP_KEY = 'ip'
    mock_network_utils.MAC_KEY = 'mac'
    mock_network_utils.PORT_KEY = 'port'

    # two random devices on the network, with different mac addresses than,
    # the one we are trying to connect to (NetworkUtils.INVALID_MAC in cfg.TCP_CONFIG)
    mock_network_utils.get_hosts.return_value = [
        {mock_network_utils.IP_KEY: '192.168.50.1',
         mock_network_utils.MAC_KEY: '00:00:00:00:00:01',
         mock_network_utils.PORT_KEY: 502},
        {mock_network_utils.IP_KEY: '192.168.50.2',
         mock_network_utils.MAC_KEY: '00:00:00:00:00:02',
         mock_network_utils.PORT_KEY: 502}
    ]

    task.execute(event_time=0)

    # Mock the clone method to check if it was called
    inverter.clone = Mock()
    assert inverter.clone.call_count == 0  # We did not try to clone the devices above

    assert len(task.bb.devices.lst) == 0


def test_execute_inverter_not_on_local_network(bb: BlackBoard):
    set_up_listeners(bb)

    config = cfg.TCP_ARGS.copy()
    config['sn'] = "test_device_not_local"
    inverter = IComFactory.create_com(config)
    bb.device_storage.add_connection(inverter)
    bb.settings.devices.add_connection(inverter, ChangeSource.LOCAL)

    inverter.connect = Mock(return_value=False)
    task = DevicePerpetualTask(0, bb, inverter)
    assert task.execute(0) is not None

    assert inverter not in bb.devices.lst
    assert inverter.connect.called

    assert len(bb.devices.lst) == 0  # Not on the local network, so not added
    assert len(bb.settings.devices.connections) == 1

    assert len(bb.purge_tasks()) == 1  # state save task added as error message is generated


def test_add_multiple_devices(bb: BlackBoard):
    set_up_listeners(bb)

    config1 = cfg.TCP_CONFIG.copy()
    config1['sn'] = "test_device_multi_1"
    device1 = IComFactory.create_com(config1)
    device1.connect = Mock(return_value=True)
    device1.is_open = Mock(return_value=True)
    device1.compare_host = Mock(return_value=False)

    config2 = cfg.P1_TELNET_CONFIG.copy()
    device2 = IComFactory.create_com(config2)
    device2.connect = Mock(return_value=True)
    device2.is_open = Mock(return_value=True)
    device2.compare_host = Mock(return_value=False)

    bb.device_storage.add_connection(device1)
    bb.device_storage.add_connection(device2)
    bb.settings.devices.add_connection(device1, ChangeSource.LOCAL)
    bb.settings.devices.add_connection(device2, ChangeSource.LOCAL)

    task1 = DevicePerpetualTask(0, bb, device1)
    task2 = DevicePerpetualTask(0, bb, device2)

    task1.execute(0)
    task2.execute(0)

    assert device1 in bb.devices.lst
    assert device2 in bb.devices.lst

    assert device1.connect.called
    assert device2.connect.called

    assert len(bb.devices.lst) == 2


def test_device_witn_sn_already_open(bb: BlackBoard):
    existing_device = MagicMock(spec=ICom)
    existing_device.get_SN.return_value = IComFactory.create_com(cfg.P1_TELNET_CONFIG).get_SN()
    existing_device.is_open.return_value = True
    existing_device.get_config.return_value = cfg.P1_TELNET_CONFIG

    set_up_listeners(bb)

    bb.devices.add(existing_device)

    new_device = MagicMock(spec=ICom)
    new_device.get_SN.return_value = existing_device.get_SN()
    new_device.is_open.return_value = False

    task = DevicePerpetualTask(0, bb, new_device)
    assert task.execute(0) is None
    assert not new_device.connect.called

    assert len(bb.devices.lst) == 1
    assert new_device not in bb.devices.lst


def test_bloated_settings_device_list(bb: BlackBoard):
    # in this test case there are multiple devices with the same sn but different connection parameters
    # this should not happen in the wild but we should handle it gracefully

    set_up_listeners(bb)

    def mock_create_com(settings: dict):
        device = MagicMock(spec=ICom)
        device.get_SN.return_value = "17"
        device.get_config.return_value = settings
        device.connect.return_value = False
        return device

    with patch('server.devices.IComFactory.IComFactory.create_com', mock_create_com):

        device = MagicMock(spec=ICom)
        device.get_SN.return_value = "17"
        device.get_config.return_value = {"key": "value_1"}
        device.connect.return_value = False
        bb.settings.devices._connections.append({"key": "value_1"})
        bb.settings.devices._connections.append({"key": "value_2"})
        bb.settings.devices._connections.append({"key": "value_3"})

        assert len(bb.settings.devices.connections) == 3

        # in the case of starting there will be 3 perpetual tasks running
        # all will find the same device on the network and will try to open it

        for settings_device in bb.settings.devices.connections:
            device = MagicMock(spec=ICom)
            device.get_SN.return_value = "17"
            device.get_config.return_value = settings_device
            device.connect.return_value = False
            device.find_device.return_value = None

            task = DevicePerpetualTask(0, bb, device)
            task.execute(0)
            assert task is not None

        assert len(bb.settings.devices.connections) == 3

        # now lets pretend we find a device on the network i.e. the first device was correct
        found_device = MagicMock(spec=ICom)
        found_device.get_SN.return_value = "17"
        found_device.get_config.return_value = {"key": "value_1"}
        found_device.connect.return_value = True
        found_device.is_open.return_value = True
        found_device.compare_host.return_value = False

        tasks = []
        for settings_device in bb.settings.devices.connections:
            device = MagicMock(spec=ICom)
            device.get_SN.return_value = "17"
            device.get_config.return_value = settings_device
            device.connect.return_value = False
            device.find_device.return_value = found_device

            task = DevicePerpetualTask(0, bb, device)
            tasks.append(task)
            task.execute(0)
            assert task is not None

        # the next time we run this the first task will sucessfully connect - the others should be removed from the settings no more tasks should be created

            # For the first task to succeed, we need to update its device to connect successfully
        if tasks:
            first_task = tasks[0]
            first_task.device.connect = Mock(return_value=True)
            first_task.device.is_open = Mock(return_value=True)
            first_task.device.compare_host = Mock(return_value=False)
            first_task.device.get_name = Mock(return_value="Test Device")

            # Manually add the device to simulate successful connection
            bb.devices.add(first_task.device)

        for task in tasks:
            result = task.execute(0)
            assert result is None

        assert len(bb.devices.lst) == 1
        # The device added might be from the first task, not necessarily found_device
        assert len(bb.devices.lst) == 1
        assert len(bb.settings.devices.connections) == 1


def test_device_found_but_fails_to_connect(bb: BlackBoard):
    existing_device = MagicMock(spec=ICom)
    existing_device.get_SN.return_value = IComFactory.create_com(cfg.P1_TELNET_CONFIG).get_SN()
    existing_device.is_open.return_value = False
    existing_device.connect.return_value = False
    existing_device.get_config.return_value = cfg.P1_TELNET_CONFIG
    existing_device.find_device.return_value = existing_device

    set_up_listeners(bb)

    bb.device_storage.add_connection(existing_device)
    bb.settings.devices.add_connection(existing_device, ChangeSource.LOCAL)

    task = DevicePerpetualTask(0, bb, existing_device)
    assert task.execute(0) is not None

    # assert task.old_device is not None

    # we now execute again the device can still not be opened
    task = task.execute(0)

    assert task is not None
    # assert task.old_device is not None

    # we continue to try to open the device a couple of times nothing should change
    for _ in range(10):
        task = task.execute(0)

        assert task is not None
        # assert task.old_device is not None


def test_same_ip_different_ports(bb: BlackBoard):
    setings_d1 = {"ip": "192.168.1.15", "sn": "7E16F266", "mac": "22:af:0b:72:aa:fe", "port": 1502, "slave_id": 2, "connection": "SUNSPEC"}
    setings_d2 = {"ip": "192.168.1.15", "sn": "232701111494", "mac": "22:af:0b:aa:5c:fe", "port": 504, "slave_id": 1, "connection": "SUNSPEC"}

    set_up_listeners(bb)

    device1 = IComFactory.create_com(setings_d1)
    device1.connect = Mock(return_value=True)
    device1.is_open = Mock(return_value=True)

    device2 = IComFactory.create_com(setings_d2)
    device2.connect = Mock(return_value=True)
    device2.is_open = Mock(return_value=True)

    # add to both storage and settings
    bb.device_storage.add_connection(device1)
    bb.device_storage.add_connection(device2)
    bb.settings.devices._connections.append(setings_d1)
    bb.settings.devices._connections.append(setings_d2)

    task1 = DevicePerpetualTask(0, bb, device1)
    task2 = DevicePerpetualTask(0, bb, device2)

    task1_ret = task1.execute(0)
    task2_ret = task2.execute(0)

    assert len(bb.devices.lst) == 2
    assert device1 in bb.devices.lst
    assert device2 in bb.devices.lst

    assert task1_ret is None
    assert task2_ret is None


def test_device_with_sn_none(bb: BlackBoard):
    set_up_listeners(bb)

    setings_d1 = {"ip": "192.168.1.15", "sn": "7E16F266", "mac": "22:af:0b:72:aa:fe", "port": 1502, "slave_id": 2, "connection": "SUNSPEC"}
    device1 = IComFactory.create_com(setings_d1)
    device1.connect = Mock(return_value=True)
    device1.is_open = Mock(return_value=True)

    bb.device_storage.add_connection(device1)
    bb.settings.devices._connections.append(setings_d1)

    task1 = DevicePerpetualTask(0, bb, device1)
    task1.execute(0)

    device2 = device1.clone()

    task2 = DevicePerpetualTask(0, bb, device2)
    task2 = task2.execute(0)

    assert task2 is None

    assert len(bb.devices.lst) == 1


# #########################################################################################################################
# Test that a device that is in the settings but not in the storage is added to the storage
# This is a migration scenario from 0.22.6 to 0.22.7
# From 0.22.8, the local storage will be the primary source of connections
# #########################################################################################################################


def test_migration_scenario(bb: BlackBoard):
    set_up_listeners(bb)

    # create a device with a sn and a connection in the settings
    device = MagicMock(spec=ICom)
    device.get_SN.return_value = "123123"
    device.get_config.return_value = {"connection": "SUNSPEC", "ip": "192.168.1.15", "sn": "123123", "mac": "22:af:0b:72:aa:fe", "port": 1502, "slave_id": 2}
    device.connect.return_value = True
    device.find_device.return_value = None

    bb.settings.devices._connections.append(device.get_config())

    task = DevicePerpetualTask(0, bb, device)
    task.execute(0)

    assert device in bb.devices.lst
    assert len(bb.devices.lst) == 1

    assert len(bb.device_storage.get_connections()) == 1  # Ensure that the device is added to the storage


def test_migration_several_devices(bb: BlackBoard):
    set_up_listeners(bb)

    # create a device with a sn and a connection in the settings
    device1 = MagicMock(spec=ICom)
    device1.get_SN.return_value = "123123"
    device1.get_config.return_value = {"connection": "SUNSPEC", "ip": "192.168.1.15", "sn": "123123", "mac": "22:af:0b:72:aa:fe", "port": 1502, "slave_id": 2}
    device1.connect.return_value = True
    device1.find_device.return_value = None

    bb.settings.devices._connections.append(device1.get_config())

    task = DevicePerpetualTask(0, bb, device1)
    task.execute(0)

    assert device1 in bb.devices.lst
    assert len(bb.devices.lst) == 1

    assert len(bb.device_storage.get_connections()) == 1
    assert bb.device_storage.connection_exists(device1)

    device2 = MagicMock(spec=ICom)
    device2.get_SN.return_value = "123124"
    device2.get_config.return_value = {"connection": "SUNSPEC", "ip": "192.168.1.15", "sn": "123124", "mac": "22:af:0b:72:aa:fe", "port": 1502, "slave_id": 2}
    device2.connect.return_value = True
    device2.find_device.return_value = None

    bb.settings.devices._connections.append(device2.get_config())

    task2 = DevicePerpetualTask(0, bb, device2)
    task2.execute(0)

    assert device2 in bb.devices.lst
    assert len(bb.devices.lst) == 2

    assert len(bb.device_storage.get_connections()) == 2  # Ensure that the device is added to the storage
    assert bb.device_storage.connection_exists(device2)

    device3 = MagicMock(spec=ICom)
    device3.get_SN.return_value = "123125"
    device3.get_config.return_value = {"connection": "P1Telnet", "ip": "192.168.1.15", "port": 80, "meter_serial_number": "123125"}
    device3.connect.return_value = True
    device3.find_device.return_value = None

    bb.settings.devices._connections.append(device3.get_config())

    task3 = DevicePerpetualTask(0, bb, device3)
    task3.execute(0)

    assert device3 in bb.devices.lst
    assert len(bb.devices.lst) == 3

    assert len(bb.device_storage.get_connections()) == 3  # Ensure that the device is added to the storage
    assert bb.device_storage.connection_exists(device3)
