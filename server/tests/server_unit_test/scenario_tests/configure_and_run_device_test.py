from server.crypto.crypto_state import CryptoState
from server.devices.ICom import ICom
import server.tasks.harvest as harvest
import server.tasks.harvestTransport as harvestTransport
from unittest.mock import MagicMock, Mock
from server.app.blackboard import BlackBoard
from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.tasks.harvestFactory import HarvestFactory
import server.tests.config_defaults as cfg


def test_harvest_from_two_devices_with_one_device_reconnection():
    # Setup
    bb = BlackBoard(Mock(spec=CryptoState))
    HarvestFactory(bb)

    # Create and connect first device
    device = MagicMock(spec=ICom)
    device.connect.return_value = True
    device.is_disconnected.return_value = False
    device.is_open.return_value = True
    device.get_SN.return_value = "device1"
    device.compare_host.return_value = False
    device.get_config.return_value = {**cfg.TCP_CONFIG, "sn": "device1"}
    
    bb.devices.add(device)
    assert device in bb.devices.lst
    
    # Create and connect second device
    device2 = MagicMock(spec=ICom)
    device2.connect.return_value = True
    device2.is_open.return_value = True
    device2.is_disconnected.return_value = False
    device2.compare_host.return_value = False
    device2.get_SN.return_value = "device2"
    device2.get_config.return_value = {**cfg.TCP_CONFIG, "sn": "device2"}
    bb.devices.add(device2)
    assert device2 in bb.devices.lst
    
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
    
    # flaky as we depend on the order of the tasks in the list
    task = ret[1]
    assert isinstance(task, DevicePerpetualTask)
    assert task.device is not None
    
    # Simulate device reconnection
    task.device.connect.return_value = True
    task.device.is_open.return_value = True
    ret = task.execute(0)
    
    assert ret is None  # Device successfully reopened
    
    # Verify final state
    assert len(bb.devices.lst) == 2
    assert len(bb.settings.devices._connections) == 2
    
    assert bb.devices.lst[0].is_open()
    assert bb.devices.lst[1].is_open()
