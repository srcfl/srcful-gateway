import server.tasks.harvest as harvest
import server.tasks.harvestTransport as harvestTransport
from unittest.mock import MagicMock
from server.blackboard import BlackBoard
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.tasks.harvestFactory import HarvestFactory


def test_harvest_from_two_devices_with_one_device_reconnection():
    # Setup
    bb = BlackBoard()
    HarvestFactory(bb)

    # Create and connect first device
    device = MagicMock()
    device.connect.return_value = True
    device.is_open.return_value = True
    device.get_SN.return_value = "00:00:00:00:00:00"
    
    task = DevicePerpetualTask(0, bb, device)
    task.execute(0)
    
    assert device in bb.devices.lst
    assert task.execute(0) is None  # Device already in the blackboard
    
    # Create and connect second device
    device2 = MagicMock()
    device2.connect.return_value = True
    device2.is_open.return_value = True
    
    task2 = DevicePerpetualTask(0, bb, device2)
    task2.execute(0)
    
    assert device2 in bb.devices.lst
    assert task2.execute(0) is None  # Device already in the blackboard
    
    # Create and execute harvest tasks for both devices
    device_harvest_task = harvest.Harvest(0, bb, device, harvestTransport.DefaultHarvestTransportFactory())
    device_harvest_task.execute(0)
    assert device.read_harvest_data.called
    
    device2_harvest_task = harvest.Harvest(0, bb, device2, harvestTransport.DefaultHarvestTransportFactory())
    device2_harvest_task.execute(0)
    assert device2.read_harvest_data.called
    
    # Simulate first device disconnection
    device.is_open.return_value = False
    assert device in bb.devices.lst
    
    # Mock device clone method
    device.clone.return_value = device
    
    # Execute harvest task for disconnected device
    ret = device_harvest_task.execute(0)
    
    assert isinstance(ret[0], DevicePerpetualTask)
    assert ret[0].device is not None
    
    # Simulate device reconnection
    ret[0].device.connect.return_value = True
    ret[0].device.is_open.return_value = True
    ret = ret[0].execute(0)
    
    assert ret is None  # Device successfully reopened
    
    # Verify final state
    assert len(bb.devices.lst) == 2
    assert len(bb.settings.devices._connections) == 2
    
    assert bb.devices.lst[0].is_open()
    assert bb.devices.lst[1].is_open()
