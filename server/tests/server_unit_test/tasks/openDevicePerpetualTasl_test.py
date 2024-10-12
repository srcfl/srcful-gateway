from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.blackboard import BlackBoard
from server.tasks.harvestFactory import HarvestFactory
from unittest.mock import MagicMock, patch
import pytest

def test_execute_invertert_added():
    bb = BlackBoard()
    HarvestFactory(bb)

    inverter = MagicMock()
    inverter.open.return_value = True
    task = DevicePerpetualTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter in bb.devices.lst
    assert inverter.connect.called
    assert ret is None
    assert bb.purge_tasks()[0] is not None


def test_retry_on_exception():
    bb = BlackBoard()
    HarvestFactory(bb)

    inverter = MagicMock()
    inverter.connect.side_effect = Exception("test")
    task = DevicePerpetualTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter.connect.called
    assert ret is task
    assert len(bb.purge_tasks()) == 0

@patch('server.network.network_utils.NetworkUtils')
def test_execute_invertert_could_not_open(mock_network_utils):
    bb = BlackBoard()
    HarvestFactory(bb)
    
    inverter = MagicMock()
    inverter.connect.return_value = False
    
    mock_network_utils.get_hosts.return_value = [{'ip': '192.168.50.1'}]

    task = DevicePerpetualTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter not in bb.devices.lst
    assert inverter.connect.called
    assert ret is task
    # assert that clone inside the task was called
    assert inverter.clone.called
    
    assert len(bb.purge_tasks()) == 1   # info message is added wich triggers a saveStateTask 


def test_execute_new_inverter_added():
    bb = BlackBoard()
    inverter = MagicMock()
    inverter.connect.return_value = False
    task = DevicePerpetualTask(0, bb, inverter)
    
    inverter2 = MagicMock()
    inverter2.is_open.return_value = True
    
    bb.devices.add(inverter2)

    task.execute(0)

    assert inverter.disconnect.called
    assert inverter not in bb.devices.lst
    assert inverter2 in bb.devices.lst


@patch('server.tasks.openDevicePerpetualTask.NetworkUtils')
def test_execute_new_inverter_added_after_rescan(mock_network_utils):
    bb = BlackBoard()
    inverter = MagicMock()
    
    inverter.connect.return_value = False
    task = DevicePerpetualTask(0, bb, inverter)

    task.execute(event_time=0)

    assert len(task.bb.devices.lst) == 0


    # Inject the mock scanner into the task
    task.scanner = mock_network_utils.get_hosts.return_value = [{'ip': '192.168.50.1'}]

    task.execute(event_time=1)

    inverter.clone.assert_called_once_with('192.168.50.1')
    inverter.connect.return_value = True

    task.execute(event_time=5001)

    assert len(task.bb.devices.lst) == 1

