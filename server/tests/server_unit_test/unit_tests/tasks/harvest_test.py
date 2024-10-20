import server.tasks.harvest as harvest
import server.tasks.harvestTransport as harvestTransport
import server.tasks.openDevicePerpetualTask as oit
from unittest.mock import Mock, patch
import pytest
from unittest.mock import MagicMock
from server.blackboard import BlackBoard
from server.settings import Settings, ChangeSource
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.tasks.openDeviceTask import OpenDeviceTask



def test_create_harvest():
    t = harvest.Harvest(0, BlackBoard(), None,  harvestTransport.DefaultHarvestTransportFactory())
    assert t is not None


def test_create_harvest_transport():
    t = harvestTransport.HarvestTransport(0, BlackBoard(), {}, {"model": "huawei"})
    assert t is not None


def test_inverter_terminated():
    mock_inverter = Mock()
    mock_inverter.is_open.return_value = False

    t = harvest.Harvest(0, BlackBoard(), mock_inverter, harvestTransport.DefaultHarvestTransportFactory())
    ret = t.execute(17)
    assert len(ret) == 1
    assert type(ret[0]) is oit.DevicePerpetualTask


def test_execute_harvest():
    mock_inverter = Mock()
    registers = {"1": "1717"}
    mock_inverter.read_harvest_data.return_value = registers
    mock_inverter.connect.return_value = True

    t = harvest.Harvest(0, BlackBoard(), mock_inverter,  harvestTransport.DefaultHarvestTransportFactory())
    ret = t.execute(17)
    assert ret is t
    assert t.barn[17] == registers
    assert len(t.barn) == 1
    assert t.time > 17

def test_execute_harvest_x10():
    # in this test we check that we get the desired behavior when we execute a harvest task 10 times
    # the first 9 times we should get the same task back
    # the 10th time we should get a list of 2 tasks back
    mock_inverter = Mock()
    registers = [{"1": 1717 + x} for x in range(10)]
    bb = BlackBoard()
    bb.settings.harvest.clear_endpoints(ChangeSource.LOCAL)
    bb.settings.harvest.add_endpoint("http://dret.com:8080", ChangeSource.LOCAL)
    t = harvest.Harvest(0, bb, mock_inverter, harvestTransport.DefaultHarvestTransportFactory())
    mock_inverter.connect.return_value = True


    for i in range(9):
        mock_inverter.read_harvest_data.return_value = registers[i]
        ret = t.execute(i)
        assert ret is t
        assert t.barn[i] == registers[i]
        assert len(t.barn) == i + 1

    mock_inverter.read_harvest_data.return_value = registers[9]
    ret = t.execute(17)
    assert len(t.barn) == 0
    assert ret is not t
    assert len(ret) == 2
    assert ret[0] is t
    assert ret[1] is not t
    assert ret[1].barn == {
        0: registers[0],
        1: registers[1],
        2: registers[2],
        3: registers[3],
        4: registers[4],
        5: registers[5],
        6: registers[6],
        7: registers[7],
        8: registers[8],
        17: registers[9],
    }

    # check that the transport has the correct post_url according to the settings
    assert ret[1].post_url == bb.settings.harvest.endpoints[0]


def _create_mock_bb():
    mock_bb = Mock()
    mock_bb.time_ms.return_value = 1000
    mock_bb.settings = Settings()
    mock_bb.settings.harvest.add_endpoint("http://localhost:8080", ChangeSource.LOCAL)
    return mock_bb

def test_execute_harvest_no_transport():
    mock_inverter = Mock()
    mock_inverter.is_terminated.return_value = False
    registers = [{"1": 1717 + x} for x in range(10)]

    mock_bb = _create_mock_bb()

    t = harvest.Harvest(0, mock_bb, mock_inverter,  harvestTransport.DefaultHarvestTransportFactory())

    for i in range(len(registers)):
        mock_inverter.read_harvest_data.return_value = registers[i]
        t = t.execute(i)

    # we should now have issued a transport and the barn should be empty
    assert len(t) == 2

    transport = t[0] if type(t[0]) is harvestTransport.HarvestTransport else t[1]
    t = t[0] if type(t[0]) is harvest.Harvest else t[1]

    assert type(transport) is harvestTransport.HarvestTransport

    assert len(t.barn) == 0
    assert len(transport.barn) == 10

def test_execute_harvest_device_terminated():
    mock_inverter = Mock()
    registers = {"1": "1717"}
    mock_inverter.read_harvest_data.return_value = registers
    mock_inverter.connect.return_value = True

    t = harvest.Harvest(0, BlackBoard(), mock_inverter,  harvestTransport.DefaultHarvestTransportFactory())
    ret = t.execute(17)
    assert ret is t
    assert t.barn[17] == registers
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


def test_execute_harvests_from_two_devices():
    bb = BlackBoard()
    device = MagicMock()
    device.connect.return_value = True
    device.is_open.return_value = True
    task = OpenDeviceTask(0, bb, device)
    task.execute(0)
    
    assert device in bb.devices.lst
    
    assert task.execute(0) is None # It is already in the blackboard
    
    # We add a second device
    device2 = MagicMock()
    device2.connect.return_value = True
    device2.is_open.return_value = True
    task2 = OpenDeviceTask(0, bb, device2)
    task2.execute(0)
    
    assert device2 in bb.devices.lst
    
    assert task2.execute(0) is None # It is already in the blackboard
    
    
    # Now we create a harvest task
    harvest_task = harvest.Harvest(0, bb, device, harvestTransport.DefaultHarvestTransportFactory())
    harvest_task.execute(0)
    
    assert device.read_harvest_data.called
    
    harvest_task2 = harvest.Harvest(0, bb, device2, harvestTransport.DefaultHarvestTransportFactory())
    harvest_task2.execute(0)
    
    assert device2.read_harvest_data.called


# Test creating a device task, then harvesting from it. Then the device unexpectedly closes and removed from the blackboard
# Then we should restart the device
def test_execute_harvests_from_two_devices_perpetual():
    bb = BlackBoard()
    device = MagicMock()
    device.connect.return_value = True
    device.is_open.return_value = True
    task = DevicePerpetualTask(0, bb, device)
    task.execute(0)
    
    assert device in bb.devices.lst
    
    assert task.execute(0) is None # It is already in the blackboard
    
    # We add a second device
    device2 = MagicMock()
    device2.connect.return_value = True
    device2.is_open.return_value = True
    task2 = DevicePerpetualTask(0, bb, device2)
    task2.execute(0)
    
    assert device2 in bb.devices.lst
    
    assert task2.execute(0) is None # It is already in the blackboard
    
    
    # Now we create a harvest task
    harvest_task = harvest.Harvest(0, bb, device, harvestTransport.DefaultHarvestTransportFactory())
    harvest_task.execute(0)
    
    assert device.read_harvest_data.called
    
    harvest_task2 = harvest.Harvest(0, bb, device2, harvestTransport.DefaultHarvestTransportFactory())
    harvest_task2.execute(0)
    
    assert device2.read_harvest_data.called
