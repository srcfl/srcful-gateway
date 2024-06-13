from server.tasks.openInverterPerpetualTask import OpenInverterPerpetualTask
from server.blackboard import BlackBoard
from server.tasks.harvestFactory import HarvestFactory
from unittest.mock import MagicMock


def test_execute_invertert_added():
    bb = BlackBoard()
    hf = HarvestFactory(bb)
    hf.dummy()
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
    hf = HarvestFactory(bb)
    hf.dummy()
    inverter = MagicMock()
    inverter.open.side_effect = Exception("test")
    task = OpenInverterPerpetualTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter.open.called
    assert ret is task
    assert len(bb.purge_tasks()) == 0


def test_execute_invertert_could_not_open():
    bb = BlackBoard()
    hf = HarvestFactory(bb)
    hf.dummy()
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


def test_execute_new_inverter_added_after_rescan():
    bb = BlackBoard()
    inverter = MagicMock()
    inverter.open.return_value = False
    task = OpenInverterPerpetualTask(0, bb, inverter)
