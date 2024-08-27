from server.tasks.openInverterPerpetualTask import OpenInverterPerpetualTask
from server.blackboard import BlackBoard
from server.tasks.harvestFactory import HarvestFactory
from unittest.mock import MagicMock, patch
from server.inverters.ModbusSolarman import ModbusSolarman
import pytest

def test_execute_invertert_added():
    bb = BlackBoard()
    HarvestFactory(bb)

    inverter = MagicMock()
    inverter.open.return_value = True
    task = OpenInverterPerpetualTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter in bb.inverters.lst
    assert inverter.open.called
    assert ret is None
    assert bb.purge_tasks()[0] is not None


def test_retry_on_exception():
    bb = BlackBoard()
    HarvestFactory(bb)

    inverter = MagicMock()
    inverter.open.side_effect = Exception("test")
    task = OpenInverterPerpetualTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter.open.called
    assert ret is task
    assert len(bb.purge_tasks()) == 0


def test_execute_invertert_could_not_open():
    bb = BlackBoard()
    HarvestFactory(bb)
    
    inverter = MagicMock()
    inverter.open.return_value = False
    task = OpenInverterPerpetualTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter not in bb.inverters.lst
    assert inverter.open.called
    assert ret is task
    assert len(bb.purge_tasks()) == 0


def test_execute_new_inverter_added():
    bb = BlackBoard()
    inverter = MagicMock()
    inverter.open.return_value = False
    task = OpenInverterPerpetualTask(0, bb, inverter)
    
    inverter2 = MagicMock()
    inverter2.is_open.return_value = True
    
    bb.inverters.add(inverter2)

    task.execute(0)

    assert inverter.terminate.called
    assert inverter not in bb.inverters.lst
    assert inverter2 in bb.inverters.lst

 
@patch('server.web.handler.get.network.ModbusScanHandler')
def test_execute_new_inverter_added_after_rescan(mock_modbus_scan_handler):
    bb = BlackBoard()
    inverter = MagicMock()
    
    inverter.open.return_value = False
    task = OpenInverterPerpetualTask(0, bb, inverter)

    task.execute(event_time=0)

    assert len(task.bb.inverters.lst) == 0
    
    # Create a mock for the scanner
    mock_scanner = mock_modbus_scan_handler.return_value
    mock_scanner.scan_ports.return_value = [{'ip': '192.168.50.1'}]

    # Inject the mock scanner into the task
    task.scanner = mock_scanner

    task.execute(event_time=1)

    inverter.clone.assert_called_once_with('192.168.50.1')
    inverter.open.return_value = True

    task.execute(event_time=5001)

    assert len(task.bb.inverters.lst) == 1

