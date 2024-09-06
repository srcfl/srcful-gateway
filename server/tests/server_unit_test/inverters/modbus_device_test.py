from server.inverters.ModbusTCP import ModbusTCP
from server.inverters.ModbusRTU import ModbusRTU
from server.inverters.ModbusSolarman import ModbusSolarman
from server.inverters.ModbusSunspec import ModbusSunspec
from server.inverters.modbus import Modbus
import server.tests.config_defaults as cfg
from server.inverters.IComFactory import IComFactory
from unittest.mock import MagicMock, patch
import pytest
from server.inverters.ICom import ICom
                
                
def test_open_and_is_open():
    devices: list[Modbus] = []
    
    tcp_conf = IComFactory.parse_connection_config_from_dict(cfg.TCP_CONFIG)
    rtu_conf = IComFactory.parse_connection_config_from_dict(cfg.RTU_CONFIG)
    solarman_conf = IComFactory.parse_connection_config_from_dict(cfg.SOLARMAN_CONFIG)
    
    devices.append(ModbusTCP(tcp_conf[1:]))
    devices.append(ModbusRTU(rtu_conf[1:]))
    devices.append(ModbusSolarman(solarman_conf[1:]))

    for device in devices:
        device.connect()
        
        with patch.object(device, '_is_open', return_value=True):
            assert device.is_open()
    
    
def test_read_harvest_no_data_exception():
        devices: list[Modbus] = []
        
        tcp_conf = IComFactory.parse_connection_config_from_dict(cfg.TCP_CONFIG)
        rtu_conf = IComFactory.parse_connection_config_from_dict(cfg.RTU_CONFIG)
        solarman_conf = IComFactory.parse_connection_config_from_dict(cfg.SOLARMAN_CONFIG)
        
        devices.append(ModbusTCP(tcp_conf[1:]))
        devices.append(ModbusRTU(rtu_conf[1:]))
        devices.append(ModbusSolarman(solarman_conf[1:]))
        
        for device in devices:
            
            def read_registers(operation, address, size):
                return [i for i in range(address, address + size)]
    
            device.read_registers = read_registers
            arr = device.read_harvest_data(True)
    
            # Empty register array should raise an exception
            with pytest.raises(Exception):
                device.read_harvest_data()
                

def test_read_harvest_data_terminated_exception():
    devices: list[Modbus] = []
    
    tcp_conf = IComFactory.parse_connection_config_from_dict(cfg.TCP_CONFIG)
    rtu_conf = IComFactory.parse_connection_config_from_dict(cfg.RTU_CONFIG)
    solarman_conf = IComFactory.parse_connection_config_from_dict(cfg.SOLARMAN_CONFIG)
    
    devices.append(ModbusTCP(tcp_conf[1:]))
    devices.append(ModbusRTU(rtu_conf[1:]))
    devices.append(ModbusSolarman(solarman_conf[1:]))

    for device in devices:
        
        with patch.object(device, 'disconnect', return_value=True):
            with pytest.raises(Exception):
                device.read_harvest_data()
                
            
def test_get_config():
    tcp_conf = IComFactory.parse_connection_config_from_dict(cfg.TCP_CONFIG)
    rtu_conf = IComFactory.parse_connection_config_from_dict(cfg.RTU_CONFIG)
    solarman_conf = IComFactory.parse_connection_config_from_dict(cfg.SOLARMAN_CONFIG)
    
    configs = [tcp_conf, rtu_conf, solarman_conf]
    
    assert ModbusTCP(tcp_conf[1:]).get_config() == cfg.TCP_CONFIG
    assert ModbusRTU(rtu_conf[1:]).get_config() == cfg.RTU_CONFIG
    assert ModbusSolarman(solarman_conf[1:]).get_config() == cfg.SOLARMAN_CONFIG


def test_modbus_device_clone():
    # Maybe move this higher up in the hierarchy, e.g. in ICom test since clone returns an ICom object? 
    devices: list[Modbus] = []
    
    tcp_conf = IComFactory.parse_connection_config_from_dict(cfg.TCP_CONFIG)
    rtu_conf = IComFactory.parse_connection_config_from_dict(cfg.RTU_CONFIG)
    solarman_conf = IComFactory.parse_connection_config_from_dict(cfg.SOLARMAN_CONFIG)
    
    devices.append(ModbusTCP(tcp_conf[1:]))
    devices.append(ModbusRTU(rtu_conf[1:]))
    devices.append(ModbusSolarman(solarman_conf[1:]))
    
    for device in devices:
        assert device.get_config() == device.clone().get_config()
        