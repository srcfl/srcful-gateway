from server.inverters.ModbusTCP import ModbusTCP
from server.inverters.ModbusRTU import ModbusRTU
from server.inverters.ModbusSolarman import ModbusSolarman
from server.inverters.ModbusSunspec import ModbusSunspec
from server.inverters.modbus import Modbus
import server.tests.config_defaults as cfg
from server.inverters.IComFactory import IComFactory
from unittest.mock import patch
import pytest 

# Patch the Sunspec connection 

@pytest.fixture
def modbus_devices():
    devices: list[Modbus] = []
    
    tcp_config = {k: v for k, v in cfg.TCP_CONFIG.items() if k != 'connection'}
    rtu_conf = {k: v for k, v in cfg.RTU_CONFIG.items() if k != 'connection'}
    solarman_conf = {k: v for k, v in cfg.SOLARMAN_CONFIG.items() if k != 'connection'}
    
    devices.append(ModbusTCP(**tcp_config))
    devices.append(ModbusRTU(**rtu_conf))
    devices.append(ModbusSolarman(**solarman_conf))

    return devices
    
                
def test_open_and_is_open(modbus_devices):
    
    for device in modbus_devices:
        device.connect()
        
        with patch.object(device, '_is_open', return_value=True):
            assert device.is_open()
    
    
def test_read_harvest_no_data_exception(modbus_devices):
        for device in modbus_devices:
            
            def read_registers(operation, address, size):
                return [i for i in range(address, address + size)]
    
            device.read_registers = read_registers
            arr = device.read_harvest_data(True)
    
            # Empty register array should raise an exception
            with pytest.raises(Exception):
                device.read_harvest_data()
                

def test_read_harvest_data_terminated_exception(modbus_devices):
    
    for device in modbus_devices:
        
        with patch.object(device, 'disconnect', return_value=True):
            with pytest.raises(Exception):
                device.read_harvest_data()
                
            
def test_get_config(modbus_devices):
    
    assert modbus_devices[0].get_config() == cfg.TCP_CONFIG
    # assert modbus_devices[1].get_config() == cfg.RTU_CONFIG
    # assert modbus_devices[2].get_config() == cfg.SOLARMAN_CONFIG


def test_modbus_device_clone(modbus_devices):
    
    
    for device in modbus_devices:
        left = device.get_config()
        right = device.clone().get_config()
        assert left == right
        

# def test_modbus_device_mac_not_present():
#     new_tcp_conf = cfg.TCP_CONFIG
#     new_tcp_conf.pop("mac")
#     tcp_conf = IComFactory.parse_connection_config_from_dict(new_tcp_conf)

#     new_solarman_conf = cfg.SOLARMAN_CONFIG
#     new_solarman_conf.pop("mac")
#     solarman_conf = IComFactory.parse_connection_config_from_dict(new_solarman_conf)
    
#     new_sunspec_conf = cfg.SUNSPEC_CONFIG
#     new_sunspec_conf.pop("mac")
#     sunspec_conf = IComFactory.parse_connection_config_from_dict(new_sunspec_conf)
    
#     devices = [ModbusTCP(tcp_conf[1:]), ModbusSolarman(solarman_conf[1:]), ModbusSunspec(sunspec_conf[1:])]
    
#     # for device in devices:
        
        
    