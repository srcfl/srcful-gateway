from server.tasks.openInverterTask import OpenInverterTask
from server.blackboard import BlackBoard
from server.tasks.harvestFactory import HarvestFactory

from unittest.mock import MagicMock


def test_execute_invertert_added():
    bb = BlackBoard()
    hf = HarvestFactory(bb)
    hf.dummy()
    inverter = MagicMock()
    inverter.open.return_value = True
    task = OpenInverterTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter in bb.inverters.lst
    assert inverter.open.called
    assert ret is None
    assert bb.purge_tasks()[0] is not None


def test_execute_invertert_could_not_open():
    bb = BlackBoard()
    hf = HarvestFactory(bb)
    hf.dummy()
    inverter = MagicMock()
    inverter.open.return_value = False
    task = OpenInverterTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter not in bb.inverters.lst
    assert inverter.open.called
    assert inverter.terminate.called
    assert ret is None
    assert len(bb.purge_tasks()) == 0

def test_execute_old_inverter_terminated():
    bb = BlackBoard()
    inverter = MagicMock()
    inverter.open.return_value = True
    task = OpenInverterTask(0, bb, inverter)
    task.execute(0)

    inverter2 = MagicMock()
    inverter2.open.return_value = True
    task = OpenInverterTask(0, bb, inverter2)
    task.execute(0)

    assert inverter.terminate.called
    assert inverter not in bb.inverters.lst
    assert inverter2 in bb.inverters.lst
    assert inverter2.open.called

def test_retry_on_exception():
    bb = BlackBoard()
    hf = HarvestFactory(bb)
    hf.dummy()
    inverter = MagicMock()
    inverter.open.side_effect = Exception("test")
    task = OpenInverterTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter.open.called
    assert ret is task
    assert len(bb.purge_tasks()) == 0