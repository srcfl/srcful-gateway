from server.tasks.openDeviceTask import OpenDeviceTask
from server.blackboard import BlackBoard
from server.tasks.harvestFactory import HarvestFactory

from unittest.mock import MagicMock


def test_execute_invertert_added():
    bb = BlackBoard()
    hf = HarvestFactory(bb)

    inverter = MagicMock()
    inverter.open.return_value = True
    task = OpenDeviceTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter in bb.devices.lst
    assert inverter.connect.called
    assert ret is None
    assert bb.purge_tasks()[0] is not None

def test_execute_inverter_already_open():
    bb = BlackBoard()
    inverter = MagicMock()
    inverter.is_open.return_value = True
    inverter.get_config.return_value = {"port": "COM1"}
    bb.devices.add(inverter)

    new_inverter = MagicMock()
    new_inverter.is_open.return_value = True
    new_inverter.get_config.return_value = {"port": "COM1"}

    task = OpenDeviceTask(0, bb, new_inverter)
    ret = task.execute(0)

    assert inverter in bb.devices.lst
    assert not inverter.connect.called
    assert not inverter.connect.called


def test_execute_invertert_could_not_open():
    bb = BlackBoard()

    inverter = MagicMock()
    inverter.connect.return_value = False
    task = OpenDeviceTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter not in bb.devices.lst
    assert inverter.connect.called
    assert inverter.disconnect.called
    assert ret is None
    assert len(bb.purge_tasks()) == 0

def test_execute_old_inverter_terminated():
    bb = BlackBoard()
    inverter = MagicMock()
    inverter.connect.return_value = True
    task = OpenDeviceTask(0, bb, inverter)
    task.execute(0)

    inverter2 = MagicMock()
    inverter2.connect.return_value = True
    task = OpenDeviceTask(0, bb, inverter2)
    task.execute(0)

    assert inverter.disconnect.called
    assert inverter not in bb.devices.lst
    assert inverter2 in bb.devices.lst
    assert inverter2.connect.called

def test_retry_on_exception():
    bb = BlackBoard()
    inverter = MagicMock()
    inverter.connect.side_effect = Exception("test")
    task = OpenDeviceTask(0, bb, inverter)
    ret = task.execute(0)

    assert inverter.connect.called
    assert ret is task
    assert len(bb.purge_tasks()) == 0