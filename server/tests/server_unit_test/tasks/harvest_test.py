import server.tasks.harvest as harvest
import server.tasks.harvestTransport as harvestTransport
import server.tasks.openInverterPerpetualTask as oit
from unittest.mock import Mock, patch
import pytest

from server.blackboard import BlackBoard


def test_create_harvest():
    t = harvest.Harvest(0, BlackBoard(), None,  harvestTransport.DefaultHarvestTransportFactory())
    assert t is not None


def test_create_harvest_transport():
    t = harvestTransport.HarvestTransport(0, BlackBoard(), {}, "huawei")
    assert t is not None


def test_inverter_terminated():
    mock_inverter = Mock()
    mock_inverter.is_terminated.return_value = True

    t = harvest.Harvest(0, BlackBoard(), mock_inverter, harvestTransport.DefaultHarvestTransportFactory())
    ret = t.execute(17)
    assert ret is None


def test_execute_harvest():
    mock_inverter = Mock()
    registers = {"1": "1717"}
    mock_inverter.read_harvest_data.return_value = registers
    mock_inverter.is_terminated.return_value = False

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
    t = harvest.Harvest(0, BlackBoard(), mock_inverter, harvestTransport.DefaultHarvestTransportFactory())
    mock_inverter.is_terminated.return_value = False

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


def test_adaptive_backoff():
    mock_inverter = Mock()
    mock_inverter.is_terminated.return_value = False
    
    mock_bb = Mock()
    mock_bb.time_ms.return_value = 1000

    t = harvest.Harvest(0, mock_bb, mock_inverter,  harvestTransport.DefaultHarvestTransportFactory())
    t.execute(17)

    assert t.backoff_time == 1966

    # Mock one failed poll -> We back off by 2 seconds instead of 1
    t.der._read_harvest_data.side_effect = Exception("mocked exception")
    t.execute(17)

    assert t.backoff_time == 3932

    # Save the initial minbackoff_time to compare with the actual minbackoff_time later on
    backoff_time = t.backoff_time

    # Number of times we want to reach max backoff time, could be anything
    num_of_lost_connections = 900

    # Now we fail until we reach max backoff time
    for _i in range(num_of_lost_connections):
        t.execute(17)
        backoff_time *= 2

        if backoff_time > 256000:
            backoff_time = 256000

        assert t.backoff_time == backoff_time
        assert t.backoff_time <= 256000


def test_adaptive_poll():
    mock_inverter = Mock()
    mock_inverter.is_terminated.return_value = False

    mock_bb = Mock()
    mock_bb.time_ms.return_value = 1000

    t = harvest.Harvest(0, mock_bb, mock_inverter, harvestTransport.DefaultHarvestTransportFactory())
    t.execute(17)

    assert t.backoff_time == 1966

    t.der._read_harvest_data.side_effect = Exception("mocked exception")
    t.backoff_time = t.max_backoff_time
    t.execute(17)

    assert t.backoff_time == 256000

    t.der._read_harvest_data.side_effect = None
    t.execute(17)

    assert t.backoff_time == 230400.0


def test_execute_harvest_no_transport():
    mock_inverter = Mock()
    mock_inverter.is_terminated.return_value = False
    registers = [{"1": 1717 + x} for x in range(10)]

    mock_bb = Mock()
    mock_bb.time_ms.return_value = 1000

    t = harvest.Harvest(0, mock_bb, mock_inverter,  harvestTransport.DefaultHarvestTransportFactory())

    for i in range(len(registers)):
        mock_inverter.read_harvest_data.return_value = registers[i]
        tasks = t.execute(i)

    # we should now have issued a transport and the barn should be empty
    assert len(tasks) == 2

    transport = tasks[0] if type(tasks[0]) is harvestTransport.HarvestTransport else tasks[1]

    assert type(transport) is harvestTransport.HarvestTransport

    assert len(t.barn) == 0
    assert len(transport.barn) == 10
  

def test_execute_harvest_incremental_backoff_increasing():
    mock_inverter = Mock()
    mock_inverter.read_harvest_data.side_effect = Exception("mocked exception")
    mock_inverter.is_terminated.return_value = False

    mock_bb = Mock()
    mock_bb.time_ms.return_value = 1000

    t = harvest.Harvest(0, mock_bb, mock_inverter,  harvestTransport.DefaultHarvestTransportFactory())

    while t.backoff_time < t.max_backoff_time:
        old_time = t.backoff_time
        ret = t.execute(17)
        assert ret is t
        assert ret.backoff_time > old_time
        assert ret.time == 17 + ret.backoff_time

    assert ret.backoff_time == t.max_backoff_time


def test_execute_harvest_incremental_backoff_reset():
    mock_inverter = Mock()
    mock_inverter.read_harvest_data.side_effect = Exception("mocked exception")
    mock_inverter.is_terminated.return_value = False
    
    mock_bb = Mock()
    mock_bb.time_ms.return_value = 1000

    t = harvest.Harvest(0, mock_bb, mock_inverter, harvestTransport.DefaultHarvestTransportFactory())

    while t.backoff_time < t.max_backoff_time:
        ret = t.execute(17)

    mock_inverter.read_harvest_data.side_effect = None
    mock_inverter.read_harvest_data.return_value = {"1": 1717}
    ret = t.execute(17)
    assert ret is t
    assert ret.time == 17 + ret.backoff_time


def test_execute_harvest_incremental_backoff_terminate_on_max():
    mock_inverter = Mock()
    mock_inverter.read_harvest_data.side_effect = Exception("mocked exception")
    mock_inverter.is_terminated.return_value = False
    
    mock_bb = Mock()
    mock_bb.time_ms.return_value = 1000

    t = harvest.Harvest(0, mock_bb, mock_inverter, harvestTransport.DefaultHarvestTransportFactory())

    while t.backoff_time < t.max_backoff_time:
        ret = t.execute(17)

    # we are now at max backoff time and the inverter should be terminated
    # the tasks returned should be t and the open inverter task
    ret = t.execute(17)
    assert len(ret) == 2
    oit_ix = 0 if type(ret[0]) is oit.OpenInverterPerpetualTask else 1
    assert type(ret[oit_ix]) is oit.OpenInverterPerpetualTask
    assert ret[(oit_ix + 1) % 2] is t

    # make sure the open inverter task has a cloned inverter
    assert mock_inverter.clone.call_count == 1
    
    # assert that inverter has been terminated
    assert t.der._terminate.call_count == 1
    mock_inverter.is_terminated.return_value = True

    # make sure we get nothing as the barn is empty
    assert t.execute(17) is None

    # Test that the execute method returns a HarvestTransport object when the has some data
    t.barn[17] = {"1": 1717}
    ret = t.execute(17)
    assert type(ret) is harvestTransport.HarvestTransport

def test_max_backoftime_leq_than_max():
    registers = [{"1": 1717 + x} for x in range(10)]
    mock_inverter = Mock()
    mock_inverter.read_harvest_data.return_value = registers[0]
    mock_inverter.is_terminated.return_value = False
    
    mock_bb = Mock()
    mock_bb.time_ms.return_value = 999999999999999999

    t = harvest.Harvest(0, mock_bb, mock_inverter, harvestTransport.DefaultHarvestTransportFactory())

    t.execute(17)  # this will cause a really long elapsed time
    assert t.backoff_time <= t.max_backoff_time


@pytest.fixture
def mock_init_chip():
    pass


@pytest.fixture
def mock_build_jwt(data, inverter_type):
    pass


@pytest.fixture
def mock_release():
    pass


@patch("server.crypto.crypto.Chip", autospec=True)
def test_data_harvest_transport_jwt(mock_chip_class):
    barn = {"test": "test"}
    inverter_type = "test"
    
    mock_chip_instance = mock_chip_class.return_value.__enter__.return_value
    mock_chip_instance.build_jwt.return_value = {str(barn), inverter_type}

    instance = harvestTransport.HarvestTransport(0, {}, barn, inverter_type)
    jwt = instance._data()

    mock_chip_instance.build_jwt.assert_called_once_with(instance.barn, instance.der_profile, 5)
    assert jwt == {str(barn), inverter_type}

def test_on_200():
    # just make the call for now
    response = Mock()

    instance = harvestTransport.HarvestTransport(0, {}, {}, "huawei")
    instance._on_200(response)


def test_on_error():
    # just make the call for now
    response = Mock()
    instance = harvestTransport.HarvestTransport(0, {}, {}, "huawei")
    instance._on_error(response)

