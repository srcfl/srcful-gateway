from server.tasks.openDeviceTask import OpenDeviceTask
from server.blackboard import BlackBoard
from server.tasks.harvestFactory import HarvestFactory
import server.tests.config_defaults as cfg

from unittest.mock import MagicMock


def test_execute_invertert_added():
    bb = BlackBoard()

    device = MagicMock()
    device.open.return_value = True
    task = OpenDeviceTask(0, bb, device)
    ret = task.execute(0)

    assert device in bb.devices.lst
    assert device.connect.called
    assert ret is None
    assert bb.purge_tasks()[0] is not None

def test_execute_inverter_already_open():
    bb = BlackBoard()
    device = MagicMock()
    device.is_open.return_value = True
    device.get_config.return_value = cfg.TCP_CONFIG
    bb.devices.add(device)

    new_device = MagicMock()
    new_device.is_open.return_value = True
    new_device.get_config.return_value = cfg.TCP_CONFIG

    task = OpenDeviceTask(0, bb, new_device)
    task.execute(0)

    assert device in bb.devices.lst
    assert not device.connect.called
    assert not device.connect.called


def test_execute_invertert_could_not_open():
    bb = BlackBoard()

    device = MagicMock()
    device.connect.return_value = False
    task = OpenDeviceTask(0, bb, device)
    ret = task.execute(0)

    assert device not in bb.devices.lst
    assert device.connect.called
    assert device.disconnect.called
    assert ret is None
    assert len(bb.purge_tasks()) == 1

def test_second_inverter_opened():
    bb = BlackBoard()
    device = MagicMock()
    device.connect.return_value = True
    task = OpenDeviceTask(0, bb, device)
    ret = task.execute(0)

    assert device in bb.devices.lst
    assert device.connect.called
    assert ret is None
    
    device2 = MagicMock()
    device2.connect.return_value = True
    task = OpenDeviceTask(0, bb, device2)
    ret = task.execute(0)

    assert device2 in bb.devices.lst
    assert device2.connect.called
    assert ret is None
    
    assert len(bb.devices.lst) == 2
    

##########################################################################################
# CONTINUE HERE 
##########################################################################################
def test_remove_device():
    bb = BlackBoard()
    device = MagicMock()
    device.connect.return_value = True
    task = OpenDeviceTask(0, bb, device)
    ret = task.execute(0)
    
    assert device in bb.devices.lst
    assert device.connect.called
    
    bb.devices.remove(device)
    
    assert device not in bb.devices.lst
    
    # assert device.disconnect.called
    

def test_retry_on_exception():
    bb = BlackBoard()
    device = MagicMock()
    device.connect.side_effect = Exception("test")
    task = OpenDeviceTask(0, bb, device)
    ret = task.execute(0)

    assert device.connect.called
    assert ret is None
    assert len(bb.purge_tasks()) == 1 # state save task added as error message is generated
    
    
def test_execute_inverter_not_on_local_network():
    bb = BlackBoard()
    device = MagicMock()
    device.connect.return_value = True
    device.get_config.return_value = cfg.TCP_CONFIG # MAC is 00:00:00:00:00:00, so probably not on the local network
    device.is_valid.return_value = False
    
    task = OpenDeviceTask(0, bb, device)
    assert task.execute(0) is None

    assert device not in bb.devices.lst
    
    assert device.connect.called
    assert device.disconnect.called

    assert len(bb.devices.lst) == 0 # Not on the local network, so not added

    assert len(bb.purge_tasks()) == 1 # state save task added as error message is generated


def test_add_multiple_devices():
    bb = BlackBoard()
    device1 = MagicMock()
    device1.connect.return_value = True
    device1.is_open.return_value = True
    

    device2 = MagicMock()
    device2.connect.return_value = True
    device2.is_open.return_value = True
    
    task1 = OpenDeviceTask(0, bb, device1)
    task2 = OpenDeviceTask(0, bb, device2)
    
    task1.execute(0)
    task2.execute(0)
    
    assert device1 in bb.devices.lst
    assert device2 in bb.devices.lst
    
    assert device1.connect.called
    assert device2.connect.called
    
    assert len(bb.devices.lst) == 2