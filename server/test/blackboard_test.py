from server.blackboard import BlackBoard
from unittest.mock import MagicMock

def test_blackboard():
    bb = BlackBoard()
    assert bb is not None
    assert bb.inverters is not None
    assert bb.inverters.lst is not None

def test_blackboard_add_inverter():
    listener = MagicMock()
    bb = BlackBoard()
    inverter = MagicMock()
    bb.inverters.addListener(listener)
    bb.inverters.add(inverter)
    assert inverter in bb.inverters.lst
    assert listener.addInverter.called

def test_blackboard_remove_inverter():
    listener = MagicMock()
    bb = BlackBoard()
    inverter = MagicMock()
    bb.inverters.addListener(listener)
    bb.inverters.add(inverter)
    bb.inverters.remove(inverter)
    assert inverter not in bb.inverters.lst
    assert listener.removeInverter.called