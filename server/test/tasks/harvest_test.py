from base64 import urlsafe_b64encode
import server.tasks.harvest as harvest
from unittest.mock import Mock, patch
import pytest


def test_createHarvest():

  t = harvest.Harvest(0, {}, None)
  assert t is not None


def test_createHarvestTransport():
  t = harvest.HarvestTransport(0, {}, {}, 'huawei')
  assert t is not None

def test_inverterTerminated():
  mockInverter = Mock()
  mockInverter.isTerminated.return_value = False
  
  t = harvest.Harvest(0, {}, mockInverter)
  t.execute(17)
  
  t.backoff_time = t.max_backoff_time
  t.inverter.readHarvestData.side_effect = Exception('mocked exception')
  t.execute(17)

  assert mockInverter.close.call_count == 1 
  assert mockInverter.open.call_count == 0

  t.inverter.is_socket_open.return_value = False

  t.execute(17)

  assert mockInverter.close.call_count == 1
  assert mockInverter.open.call_count == 1

  

def test_executeHarvest():
  mockInverter = Mock()
  registers = {'1': '1717'}
  mockInverter.readHarvestData.return_value = registers
  mockInverter.isTerminated.return_value = False

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
  mockInverter.isTerminated.return_value = False

  for i in range(9):
    mockInverter.readHarvestData.return_value = registers[i]
    ret = t.execute(i)
    assert ret is t
    assert t.barn[i] == registers[i]
    assert len(t.barn) == i + 1

  mockInverter.readHarvestData.return_value = registers[9]
  ret = t.execute(17)
  assert len(t.barn) == 0
  assert ret is not t
  assert len(ret) == 2
  assert ret[0] is t
  assert ret[1] is not t
  assert ret[1].barn == {0: registers[0], 1: registers[1], 2: registers[2], 3: registers[3],
                         4: registers[4], 5: registers[5], 6: registers[6], 7: registers[7], 8: registers[8], 17: registers[9]}

def test_adaptiveBackoff():
  mockInverter = Mock()
  mockInverter.isTerminated.return_value = False
  
  t = harvest.Harvest(0, {}, mockInverter)
  t.execute(17)

  assert t.backoff_time == 1000

  # Mock one failed poll -> We back off by 2 seconds instead of 1
  t.inverter.readHarvestData.side_effect = Exception('mocked exception')
  t.execute(17)

  assert t.backoff_time == 2000

  # Save the initial minbackoff_time to compare with the actual minbackoff_time later on
  backoff_time = t.backoff_time

  # Number of times we want to reach max backoff time, could be anything
  num_of_lost_connections = 900

  # Now we fail until we reach max backoff time
  for i in range(num_of_lost_connections):
    t.execute(17)
    backoff_time *=2

    if backoff_time > 300000:
      backoff_time = 300000
    
    assert t.backoff_time == backoff_time 
    assert t.backoff_time <= 300000


def test_adaptivePoll():
  mockInverter = Mock()
  mockInverter.isTerminated.return_value = False
  
  t = harvest.Harvest(0, {}, mockInverter)
  t.execute(17)

  assert t.backoff_time == 1000


  t.inverter.readHarvestData.side_effect = Exception('mocked exception')
  t.backoff_time = t.max_backoff_time
  t.execute(17)

  assert t.backoff_time == 300000

  t.inverter.readHarvestData.side_effect = None 
  t.execute(17)

  assert t.backoff_time == 270000.0


  
    



def test_executeHarvestNoTransport():
  mockInverter = Mock()
  mockInverter.isTerminated.return_value = False
  registers = [{'1': 1717 + x} for x in range(10)]
  t = harvest.Harvest(0, {}, mockInverter)

  for i in range(len(registers)):
    mockInverter.readHarvestData.return_value = registers[i]
    t.execute(i)

  # we should now have issued a transport and the barn should be empty
  assert t.transport is not None
  assert len(t.barn) == 0

  # we now continue to harvest but these should not be transported as the transport task is not executed
  for i in range(len(registers)):
    mockInverter.readHarvestData.return_value = registers[i]
    t.execute(i + 100)

  assert len(t.barn) == 10

  # finally we fake that the barn has been transported and we should get a new transport task
  # note that we only transport every 10th harvest
  t.transport.reply = "all done"
  for i in range(len(registers)):
    mockInverter.readHarvestData.return_value = registers[i]
    ret = t.execute(i + 200)
  assert len(t.barn) == 0
  assert ret is not t
  assert len(ret) == 2
  assert ret[0] is t
  assert ret[1] is not t



def test_executeHarvest_incrementalBackoff_increasing():
  mockInverter = Mock()
  mockInverter.readHarvestData.side_effect = Exception('mocked exception')
  mockInverter.isTerminated.return_value = False
  t = harvest.Harvest(0, {}, mockInverter)
 
  while t.backoff_time < t.max_backoff_time:
    oldTime = t.backoff_time 
    ret = t.execute(17)
    assert ret is t
    assert ret.backoff_time > oldTime
    assert ret.time == 17 + ret.backoff_time

  assert ret.backoff_time == t.max_backoff_time

def test_executeHarvest_incrementalBackoff_reset():
  mockInverter = Mock()
  mockInverter.readHarvestData.side_effect = Exception('mocked exception')
  mockInverter.isTerminated.return_value = False
  t = harvest.Harvest(0, {}, mockInverter)
 
  while t.backoff_time < t.max_backoff_time:
    ret = t.execute(17)

  mockInverter.readHarvestData.side_effect = None
  mockInverter.readHarvestData.return_value = {'1': 1717}
  ret = t.execute(17)
  assert ret is t
  assert ret.time == 17 + ret.backoff_time

def test_executeHarvest_incrementalBackoff_reconnectOnMax():
  mockInverter = Mock()
  mockInverter.readHarvestData.side_effect = Exception('mocked exception')
  mockInverter.isTerminated.return_value = False
  t = harvest.Harvest(0, {}, mockInverter)
 
  while t.backoff_time < t.max_backoff_time:
    ret = t.execute(17)

  # assert that the inverter has not been closed and opened again
    assert mockInverter.close.call_count == 0
  assert mockInverter.open.call_count == 0

  ret = t.execute(17)
  assert ret is t

  t.inverter.is_socket_open.return_value = False

  t.execute(17)

  # assert that inverter has been closed and opened again
  assert mockInverter.close.call_count == 1
  assert mockInverter.open.call_count == 1


@pytest.fixture
def mock_initChip():
  pass


@pytest.fixture
def mock_buildJWT(data, inverter_type):
  pass


@pytest.fixture
def mock_release():
  pass


@patch('server.crypto.crypto.initChip')
@patch('server.crypto.crypto.buildJWT')
@patch('server.crypto.crypto.release')
def test_dataHarvestTransport(mock_release, mock_buildJWT, mock_initChip):
  barn = {'test': 'test'}
  inverter_type = 'test'
  mock_buildJWT.return_value = {str(barn), inverter_type}

  instance = harvest.HarvestTransport(0, {}, barn, inverter_type)
  result = instance._data()

  mock_initChip.assert_called_once()
  mock_buildJWT.assert_called_once_with(instance.barn, instance.inverter_type)
  mock_release.assert_called_once()
  result == str(barn)


def test_on200():
  # just make the call for now
  response = Mock()

  instance = harvest.HarvestTransport(0, {}, {}, 'huawei')
  instance._on200(response)


def test_onError():
  # just make the call for now
  response = Mock()
  instance = harvest.HarvestTransport(0, {}, {}, 'huawei')
  instance._onError(response)


