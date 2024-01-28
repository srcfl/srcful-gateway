from server.tasks.openInverterTask import OpenInverterTask
from server.blackboard import BlackBoard

from unittest.mock import MagicMock


def test_execute_invertert_added():
    bb = BlackBoard()
    inverter = MagicMock()
    inverter.open.return_value = True
    task = OpenInverterTask(0, bb, inverter)
    harvest = task.execute(0)

    assert inverter in bb.inverters.lst
    assert inverter.open.called
    assert harvest is not None


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
