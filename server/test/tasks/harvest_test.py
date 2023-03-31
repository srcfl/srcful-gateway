from base64 import urlsafe_b64encode
import server.tasks.harvest as harvest
from unittest.mock import Mock, patch
import pytest


def test_createHarvest():
    t = harvest.Harvest(0, {}, None)
    assert t is not None


def test_createHarvestTransport():
    t = harvest.HarvestTransport(0, {}, {})
    assert t is not None


def test_executeHarvest():
    mockInverter = Mock()
    registers = {'1': '1717'}
    mockInverter.read.return_value = registers

    t = harvest.Harvest(0, {}, mockInverter)
    ret = t.execute(17)
    assert ret is t
    assert t.barn[17] == registers
    assert len(t.barn) == 1
    assert t.time == 17 + 1000


def test_executeHarvestx10():
    # in this test we check that we get the desired behavior when we execute a harvest task 10 times
    # the first 9 times we should get the same task back
    # the 10th time we should get a list of 2 tasks back
    mockInverter = Mock()
    registers = [{'1': 1717 + x} for x in range(10)]
    t = harvest.Harvest(0, {}, mockInverter)

    for i in range(9):
        mockInverter.read.return_value = registers[i]
        ret = t.execute(i)
        assert ret is t
        assert t.barn[i] == registers[i]
        assert len(t.barn) == i + 1

    mockInverter.read.return_value = registers[9]
    ret = t.execute(17)
    assert len(t.barn) == 0
    assert ret is not t
    assert len(ret) == 2
    assert ret[0] is t
    assert ret[1] is not t
    assert ret[1].barn == {0: registers[0], 1: registers[1], 2: registers[2], 3: registers[3],
                           4: registers[4], 5: registers[5], 6: registers[6], 7: registers[7], 8: registers[8], 17: registers[9]}


def test_executeHarvestNoTransport():
    mockInverter = Mock()
    registers = [{'1': 1717 + x} for x in range(10)]
    t = harvest.Harvest(0, {}, mockInverter)

    for i in range(len(registers)):
        mockInverter.read.return_value = registers[i]
        t.execute(i)

    # we should now have issued a transport and the barn should be empty
    assert t.transport is not None
    assert len(t.barn) == 0

    # we now continue to harvest but these should not be transported as the transport task is not executed
    for i in range(len(registers)):
        mockInverter.read.return_value = registers[i]
        t.execute(i + 100)

    assert len(t.barn) == 10

    # finally we fake that the barn has been transported and we should get a new transport task
    # note that we only transport every 10th harvest
    t.transport.reply = "all done"
    for i in range(len(registers)):
        mockInverter.read.return_value = registers[i]
        ret = t.execute(i + 200)
    assert len(t.barn) == 0
    assert ret is not t
    assert len(ret) == 2
    assert ret[0] is t
    assert ret[1] is not t


def test_executeHarvest_failedRead():
    mockInverter = Mock()
    mockInverter.read.side_effect = Exception('mocked exception')

    t = harvest.Harvest(0, {}, mockInverter)
    ret = t.execute(17)
    assert ret is None


@pytest.fixture
def mock_initChip():
    pass


@pytest.fixture
def mock_buildJWT(data):
    pass


@pytest.fixture
def mock_release():
    pass


@patch('server.crypto.crypto.initChip')
@patch('server.crypto.crypto.buildJWT')
@patch('server.crypto.crypto.release')
def test_dataHarvestTransport(mock_release, mock_buildJWT, mock_initChip):
    barn = {'test': 'test'}
    mock_buildJWT.return_value = str(barn)

    instance = harvest.HarvestTransport(0, {}, barn)
    result = instance._data()

    mock_initChip.assert_called_once()
    mock_buildJWT.assert_called_once_with(instance.barn)
    mock_release.assert_called_once()
    result == str(barn)


def test_on200():
    # just make the call for now
    response = Mock()

    instance = harvest.HarvestTransport(0, {}, {})
    instance._on200(response)


def test_onError():
    # just make the call for now
    response = Mock()
    instance = harvest.HarvestTransport(0, {}, {})
    instance._onError(response)
