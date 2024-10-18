from server.devices.ModbusTCP import ModbusTCP
from server.devices.ModbusRTU import ModbusRTU
from server.devices.ModbusSunspec import ModbusSunspec
from server.devices.ModbusSolarman import ModbusSolarman
from server.devices.modbus import Modbus
from server.devices.ICom import ICom
import server.tests.config_defaults as cfg
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
    assert modbus_devices[1].get_config() == cfg.RTU_CONFIG
    assert modbus_devices[2].get_config() == cfg.SOLARMAN_CONFIG


def test_modbus_device_clone(modbus_devices):
    
    
    for device in modbus_devices:
        left = device.get_config()
        right = device.clone().get_config()
        assert left == right
        

def test_modbus_device_mac_not_present(modbus_devices):

   for device in modbus_devices:
        config = device.get_config()
       
        if config[ICom.CONNECTION_KEY] == "TCP":
            config.pop(ICom.CONNECTION_KEY)
            device = ModbusTCP(**config)
        elif config[ICom.CONNECTION_KEY] == "SOLARMAN":
            config.pop(ICom.CONNECTION_KEY)
            device = ModbusSolarman(**config)
        elif config[ICom.CONNECTION_KEY] == "SUNSPEC":
            config.pop(ICom.CONNECTION_KEY)
            device = ModbusSunspec(**config)
        else: 
            continue # Not an IP-based connection
            
        config = device.get_config()
        assert device.mac is not None
        assert config["mac"] == "00:00:00:00:00:00"
    
    
def test_get_SN(modbus_devices):
    
    modbus_tcp = modbus_devices[0]
    modbus_rtu = modbus_devices[1]
    modbus_solarman = modbus_devices[2]
    
    assert modbus_tcp.get_SN() == "00:00:00:00:00:00" # Modbus Device MAC-Address
    assert modbus_rtu.get_SN() == "N/A" # Not implemented yet
    assert modbus_solarman.get_SN() == 1234567890 # Stick Logger SN
        
        