from server.tasks.openDevicePerpetualTask import DevicePerpetualTask
from server.blackboard import BlackBoard
from server.tasks.harvestFactory import HarvestFactory
from unittest.mock import MagicMock, patch
from server.devices.modbus import Modbus
from server.devices.ModbusTCP import ModbusTCP
from server.devices.ModbusRTU import ModbusRTU
from server.devices.ModbusSolarman import ModbusSolarman
import server.tests.config_defaults as cfg
import pytest 

@pytest.fixture
def modbus_devices():
    devices: list[Modbus] = []
    
    tcp_config = {k: v for k, v in cfg.TCP_CONFIG.items() if k != 'connection'}
    rtu_conf = {k: v for k, v in cfg.RTU_CONFIG.items() if k != 'connection'}
    solarman_conf = {k: v for k, v in cfg.SOLARMAN_CONFIG.items() if k != 'connection'}
    
    devices.append(ModbusTCP(**tcp_config))
    devices.append(ModbusRTU(**rtu_conf))
    devices.append(ModbusSolarman(**solarman_conf))
    

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

def test_execute_inverter_not_found():
    bb = BlackBoard()
    HarvestFactory(bb)
    
    device = MagicMock()
    device.connect.return_value = False
    device.get_config.return_value = cfg.TCP_CONFIG

    device.find_device.return_value = None # Device not found on the network
    
    task = DevicePerpetualTask(0, bb, device)
    ret = task.execute(0)
    
    assert ret is task
    assert task.time == 300000 # execute run again in 5 minutes
    
    assert len(bb.purge_tasks()) == 1   # info message is added wich triggers a saveStateTask
    

def test_execute_new_inverter_added_after_rescan():
    bb = BlackBoard()
    inverter = MagicMock()
    inverter.get_config.return_value = cfg.TCP_CONFIG
    inverter.connect.return_value = False
    
    task = DevicePerpetualTask(0, bb, inverter)

    task.execute(event_time=0)
    
    inverter.connect.return_value = True
    
    ret = task.execute(event_time=500)
    
    assert ret is None
    assert len(bb.devices.lst) == 1
    
    
@patch('server.tasks.openDevicePerpetualTask.NetworkUtils')
def test_reconnect_does_not_find_known_device(mock_network_utils):
    bb = BlackBoard()
    HarvestFactory(bb)
    
    inverter = MagicMock()
    inverter.get_config.return_value = cfg.TCP_CONFIG
    inverter.connect.return_value = False
    task = DevicePerpetualTask(0, bb, inverter)
    
    mock_network_utils.IP_KEY = 'ip'
    mock_network_utils.MAC_KEY = 'mac'
    mock_network_utils.PORT_KEY = 'port'
    
    # two random devices on the network, with different mac addresses than,
    # the one we are trying to connect to (00:00:00:00:00:00 in cfg.TCP_CONFIG)
    mock_network_utils.get_hosts.return_value = [
        {mock_network_utils.IP_KEY: '192.168.50.1',
         mock_network_utils.MAC_KEY: '00:00:00:00:00:01',
         mock_network_utils.PORT_KEY: 502},
        {mock_network_utils.IP_KEY: '192.168.50.2',
         mock_network_utils.MAC_KEY: '00:00:00:00:00:02',
         mock_network_utils.PORT_KEY: 502}
    ]
    
    task.execute(event_time=0)
    
    assert inverter.clone.call_count == 0 # We did not try to clone the devices above
    
    assert len(task.bb.devices.lst) == 0


def test_execute_inverter_not_on_local_network():
    bb = BlackBoard()
    inverter = MagicMock()
    inverter.connect.return_value = True
    inverter.get_config.return_value = cfg.TCP_CONFIG # MAC is 00:00:00:00:00:00, so probably not on the local network
    inverter.is_valid.return_value = False
    task = DevicePerpetualTask(0, bb, inverter)
    assert task.execute(0) is None

    assert inverter not in bb.devices.lst
    assert inverter.connect.called
    assert inverter.disconnect.called

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
    
    task1 = DevicePerpetualTask(0, bb, device1)
    task2 = DevicePerpetualTask(0, bb, device2)
    
    task1.execute(0)
    task2.execute(0)
    
    assert device1 in bb.devices.lst
    assert device2 in bb.devices.lst
    
    assert device1.connect.called
    assert device2.connect.called
    
    assert len(bb.devices.lst) == 2
    
    

