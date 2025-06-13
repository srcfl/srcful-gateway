import json
import time
from server.crypto.crypto_state import CryptoState
from server.devices.ICom import DeviceMode, HarvestDataType, ICom
from server.tasks import deviceTask
import server.tasks.harvest as harvest
import server.tasks.harvestTransport as harvestTransport
import server.tasks.openDevicePerpetualTask as oit
from unittest.mock import Mock, patch
import pytest
from unittest.mock import MagicMock
from server.app.blackboard import BlackBoard
from server.app.settings import Settings, ChangeSource
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.tasks.openDeviceTask import OpenDeviceTask


@pytest.fixture
def blackboard():
    return BlackBoard(Mock(spec=CryptoState))


def test_create_harvest(blackboard: BlackBoard):
    t = harvest.Harvest()
    assert t is not None


def test_create_harvest_transport(blackboard: BlackBoard):
    t = harvestTransport.HarvestTransport(0, blackboard, {}, {"model": "huawei"})
    assert t is not None


# TODO: Move to deviceTask test
def test_inverter_terminated(blackboard: BlackBoard):
    mock_inverter = Mock()
    mock_inverter.is_open.return_value = False
    mock_inverter.is_disconnected.return_value = False

    t = deviceTask.DeviceTask(0, blackboard, mock_inverter, harvestTransport.DefaultHarvestTransportFactory())
    ret = t.execute(17)
    assert len(ret) == 1
    assert type(ret[0]) is oit.DevicePerpetualTask


# TODO: Move to deviceTask test
def test_execute_device_task(blackboard: BlackBoard):
    mock_inverter = Mock(spec=ICom)
    registers = {"1": "1717"}
    mock_inverter.read_harvest_data.return_value = registers
    mock_inverter.connect.return_value = True
    mock_inverter.get_backoff_time_ms.return_value = 1000
    mock_inverter.get_device_mode.return_value = DeviceMode.READ


    t = deviceTask.DeviceTask(0, blackboard, mock_inverter,  harvestTransport.DefaultHarvestTransportFactory())
    ret = t.execute(17)
    assert t in ret
    assert t.barn[max(t.barn.keys())] == registers
    assert len(t.barn) == 1
    assert t.time > 17


# TODO: Move to deviceTask test
def test_execute_device_task_transport_on_long_interval(blackboard: BlackBoard):
    mock_inverter = Mock(spec=ICom)
    mock_inverter.connect.return_value = True
    mock_inverter.get_backoff_time_ms.return_value = 10  # 10 mseconds
    mock_inverter.read_harvest_data.return_value = {"0": "1337"}
    mock_inverter.get_device_mode.return_value = DeviceMode.READ

    blackboard.time_ms = Mock(return_value=1000)
    t = deviceTask.DeviceTask(0, blackboard, mock_inverter, harvestTransport.DefaultHarvestTransportFactory())

    blackboard.time_ms.return_value += 10000  # that the time has passed 10 seconds after a long harvest.
    ret = t.execute(17)
    assert len(ret) == 2
    assert t in ret
    assert len(t.barn) == 0
    assert t.time > 17


def test_execute_device_task_10s(blackboard: BlackBoard):
    # in this test we check that we get the desired behavior when we execute a device task 10 times
    # the first 9 times we should get the same task back
    # the 10th time we should get a list of 2 tasks back
    mock_inverter = Mock(spec=ICom)
    registers = [{"1": 1717 + x} for x in range(11)]
    bb = blackboard
    bb.settings.harvest.clear_endpoints(ChangeSource.LOCAL)
    bb.settings.harvest.add_endpoint("http://dret.com:8080", ChangeSource.LOCAL)
    bb.time_ms = Mock(return_value=1000)
    t = deviceTask.DeviceTask(0, bb, mock_inverter, harvestTransport.DefaultHarvestTransportFactory())
    mock_inverter.connect.return_value = True
    mock_inverter.get_backoff_time_ms.return_value = 1000
    mock_inverter.get_device_mode.return_value = DeviceMode.READ

    index_time_map = {}

    for i in range(10):
        mock_inverter.read_harvest_data.return_value = registers[i]
        ret = t.execute(i)
        assert t in ret
        # the largest key is the last one
        assert t.barn[max(t.barn.keys())] == registers[i]
        assert len(t.barn) == i + 1
        index_time_map[i] = max(t.barn.keys())
        bb.time_ms.return_value += 1000

    mock_inverter.read_harvest_data.return_value = registers[10]
    ret = t.execute(17)
    assert len(t.barn) == 0
    assert ret is not t
    assert len(ret) == 2
    assert ret[0] is t
    assert ret[1] is not t
    assert t.harvest_count == 11
    expected_barn = {
        index_time_map[0]: registers[0],
        index_time_map[1]: registers[1],
        index_time_map[2]: registers[2],
        index_time_map[3]: registers[3],
        index_time_map[4]: registers[4],
        index_time_map[5]: registers[5],
        index_time_map[6]: registers[6],
        index_time_map[7]: registers[7],
        index_time_map[8]: registers[8],
        index_time_map[9]: registers[9],
        max(ret[1].barn.keys()): registers[10],
    }

    assert ret[1].barn == expected_barn

    # check that the transport has the correct post_url according to the settings
    assert ret[1].post_url == bb.settings.harvest.endpoints[0]


def _create_mock_bb():
    mock_bb = Mock(spec=BlackBoard)
    mock_bb.time_ms.return_value = 1000
    mock_bb.settings = Settings()
    mock_bb.settings.harvest.add_endpoint("http://localhost:8080", ChangeSource.LOCAL)
    return mock_bb


def test_execute_harvest_no_transport():
    mock_inverter = Mock(spec=ICom)
    mock_inverter.is_disconnected.return_value = False
    mock_inverter.get_backoff_time_ms.return_value = 1000
    mock_inverter.get_device_mode.return_value = DeviceMode.READ

    registers = [{"1": 1717 + x} for x in range(11)]

    mock_bb = _create_mock_bb()

    t = [deviceTask.DeviceTask(0, mock_bb, mock_inverter,  harvestTransport.DefaultHarvestTransportFactory())]

    for i in range(len(registers)):
        mock_inverter.read_harvest_data.return_value = registers[i]
        mock_bb.time_ms.return_value = 1000 + i * 1000
        t = t[0].execute(i)

    # we should now have issued a transport and the barn should be empty
    assert len(t) == 2

    transport = t[0] if type(t[0]) is harvestTransport.HarvestTransport else t[1]
    t = t[0] if type(t[0]) is deviceTask.DeviceTask else t[1]

    assert type(transport) is harvestTransport.HarvestTransport

    assert len(t.barn) == 0
    assert len(transport.barn) == 11


def test_execute_harvest_device_terminated():
    mock_inverter = Mock(spec=ICom)
    registers = {"1": "1717"}
    mock_inverter.read_harvest_data.return_value = registers
    mock_inverter.connect.return_value = True
    mock_inverter.get_backoff_time_ms.return_value = 1000
    mock_inverter.get_device_mode.return_value = DeviceMode.READ

    t = deviceTask.DeviceTask(0, BlackBoard(Mock(spec=CryptoState)), mock_inverter,  harvestTransport.DefaultHarvestTransportFactory())
    ret = t.execute(17)
    assert t in ret
    assert t.barn[max(t.barn.keys())] == registers
    assert len(t.barn) == 1
    assert t.time > 17

    mock_inverter.read_harvest_data.side_effect = Exception("mocked exception")
    ret = t.execute(17)
    assert len(ret) == 2


@pytest.fixture
def mock_init_chip():
    pass


@pytest.fixture
def mock_build_jwt(data, haeders):
    pass


@pytest.fixture
def mock_release():
    pass


@patch("server.crypto.crypto.Chip", autospec=True)
def test_data_harvest_transport_jwt(mock_chip_class):
    barn = {"test": "test"}

    headers = {"model": "volvo 240", "dtype": "unknown"}

    mock_chip_instance = mock_chip_class.return_value.__enter__.return_value
    mock_chip_instance.build_jwt.return_value = {str(barn), str(headers)}

    instance = harvestTransport.HarvestTransport(0, {}, barn, headers)
    jwt = instance._data()

    mock_chip_instance.build_jwt.assert_called_once_with(instance.barn, headers, 5)
    assert jwt == {str(barn), str(headers)}


def test_on_200():
    # just make the call for now
    response = Mock()
    headers = {"model": "volvo 240", "dtype": "unknown"}

    instance = harvestTransport.HarvestTransport(0, {}, {}, headers)
    instance._on_200(response)


def test_on_error():
    # just make the call for now
    response = Mock()
    headers = {"model": "volvo 240", "dtype": "unknown"}

    instance = harvestTransport.HarvestTransport(0, {}, {}, headers)
    instance._on_error(response)


def test_execute_harvests_from_two_devices(blackboard: BlackBoard):
    device = MagicMock()
    device.connect.return_value = True
    device.is_open.return_value = True
    device.compare_host.return_value = False
    device.get_backoff_time_ms.return_value = 1000
    device.get_device_mode.return_value = DeviceMode.READ
    task = OpenDeviceTask(0, blackboard, device)
    task.execute(0)

    assert device in blackboard.devices.lst

    assert task.execute(0) is None  # It is already in the blackboard

    # We add a second device
    device2 = MagicMock()
    device2.connect.return_value = True
    device2.is_open.return_value = True
    device2.compare_host.return_value = False
    device2.get_backoff_time_ms.return_value = 1000
    device2.get_device_mode.return_value = DeviceMode.READ
    task2 = OpenDeviceTask(0, blackboard, device2)
    task2.execute(0)

    assert device2 in blackboard.devices.lst

    assert task2.execute(0) is None  # It is already in the blackboard

    # Now we create a harvest task
    harvest_task = deviceTask.DeviceTask(0, blackboard, device, harvestTransport.DefaultHarvestTransportFactory())
    harvest_task.execute(0)

    assert device.read_harvest_data.called

    harvest_task2 = deviceTask.DeviceTask(0, blackboard, device2, harvestTransport.DefaultHarvestTransportFactory())
    harvest_task2.execute(0)

    assert device2.read_harvest_data.called


def test_create_headers(blackboard: BlackBoard):
    device = MagicMock(spec=ICom)
    device.get_harvest_data_type.return_value = HarvestDataType.MODBUS_REGISTERS
    device.get_SN.return_value = "1234567890"
    device.get_name.return_value = "Volvo 240"
    device.get_device_mode.return_value = DeviceMode.READ

    harvest_task = deviceTask.DeviceTask(0, blackboard, device, harvestTransport.DefaultHarvestTransportFactory())

    headers = harvest_task._create_transport_headers(device)

    #  check so the headers can be json serialized
    try:
        json.dumps(headers)
    except Exception as e:
        assert False


def test_closed_device_disconnection(blackboard: BlackBoard):
    # Setup mock device
    mock_device = Mock(spec=ICom)
    mock_device.is_open.return_value = False  # Device is closed
    mock_device.is_disconnected.return_value = False  # But not disconnected
    mock_device.clone.return_value = mock_device
    mock_device.get_device_mode.return_value = DeviceMode.READ

    # Create harvest task
    task = deviceTask.DeviceTask(0, blackboard, mock_device, harvestTransport.DefaultHarvestTransportFactory())

    # Execute the task
    result = task.execute(17)

    # Verify disconnect was called
    mock_device.disconnect.assert_called_once()

    # Verify we got back the expected tasks
    assert len(result) >= 1  # Should have at least the DevicePerpetualTask
    assert any(isinstance(t, DevicePerpetualTask) for t in result)
