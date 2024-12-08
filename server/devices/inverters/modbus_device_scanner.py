from typing import List, Optional
import struct
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from server.network.network_utils import HostInfo, NetworkUtils
from server.devices.ICom import ICom
from server.devices.supported_devices.profiles import ModbusProfile, ModbusDeviceProfiles
from server.devices.profile_keys import ProtocolKey
from server.devices.inverters.ModbusTCP import ModbusTCP
from pymodbus.exceptions import ModbusIOException
from server.devices.supported_devices.profiles import RegisterInterval
import time



logger = logging.getLogger(__name__)


"""
1. Scan the network for hosts with open Modbus ports
2. For each host in parallel, try to identify the device using different profiles
3. For each profile sequentially, try different slave IDs
4. If a valid frequency reading is obtained, return the device

scan_for_modbus_devices()  # Entry point
│
├─── ThreadPoolExecutor (max_workers=32)
│    │
│    ├─── Host1 Thread [identify_device()] ─── Sequential Profile Testing
│    │                                         ├─── Profile1 -> Try Slave IDs 0-5
│    │                                         ├─── Profile2 -> Try Slave IDs 0-5
│    │                                         └─── Profile3 -> Try Slave IDs 0-5...
│    │
│    ├─── Host2 Thread [identify_device()] ─── Sequential Profile Testing
│    │                                         ├─── Profile1 -> Try Slave IDs 0-5
│    │                                         ├─── Profile2 -> Try Slave IDs 0-5
│    │                                         └─── Profile3 -> Try Slave IDs 0-5...
│    │
│    └─── Host3 Thread [identify_device()] ─── Sequential Profile Testing
│                                             ├─── Profile1 -> Try Slave IDs 0-5
│                                             ├─── Profile2 -> Try Slave IDs 0-5
│                                             └─── Profile3 -> Try Slave IDs 0-5...
│
└─── Main Thread (waits for completion)
     └── Returns list of found devices
"""


def scan_for_modbus_devices(ports: List[int]) -> List[ICom]:
    """
    Scan the network for Modbus TCP devices and try to identify their make/model
    by reading the frequency register.
    """
    devices: List[ICom] = []
    
    # Scan network for hosts with open Modbus ports
    hosts = NetworkUtils.get_hosts(ports=ports)
    
    if not hosts:
        logger.debug("No hosts found with open Modbus ports")
        return devices

    # Use ThreadPoolExecutor for parallel host scanning only
    with ThreadPoolExecutor(max_workers=min(32, len(hosts))) as executor:
        future_to_host = {
            executor.submit(identify_device, host): host 
            for host in hosts
        }
        
        for future in as_completed(future_to_host):
            host = future_to_host[future]
            try:
                device = future.result()
                if device:
                    devices.append(device)
            except Exception as e:
                logger.error(f"Error identifying device at {host.ip}:{host.port}: {str(e)}")
    
    # Log summary of found devices
    logger.debug("==============================================================================")
    logger.debug(f"Modbus Scan Complete - Found {len(devices)} devices:")
    if devices:
        for device in devices:
            logger.debug(f"- {device.device_type} at {device.ip}:{device.port} (Slave ID: {device.slave_id})")
    else:
        logger.debug("No devices found")
    logger.debug("==============================================================================")
                
    return devices

def identify_device(host: HostInfo) -> Optional[ICom]:
    """
    Try to identify a device by testing profiles sequentially, then slave IDs sequentially.
    This function runs in parallel for different hosts.
    """
    profiles: List[ModbusProfile] = ModbusDeviceProfiles().get_supported_devices()
    
    # Test each profile sequentially
    for profile in profiles:
        # Skip profiles that are not Modbus or don't have any registers
        if profile.protocol != ProtocolKey.MODBUS or not profile.registers:
            continue
            
        freq_register: RegisterInterval = profile.registers[0]
        
        # Test each slave ID sequentially for this profile
        for slave_id in range(6):  # 0-5
            try:
                device = ModbusTCP(
                    ip=host.ip,
                    port=host.port,
                    mac=host.mac,
                    slave_id=slave_id,
                    device_type=profile.name
                )
                
                # Try to connect and read frequency
                if device.connect():
                    frequency = read_frequency(
                        device,
                        freq_register.operation,
                        freq_register.start_register,
                        freq_register.offset,
                        freq_register.scale_factor
                    )
                    
                    # If we got a valid frequency reading (typically 45-65 Hz)
                    if 47 <= frequency <= 63:
                        logger.info(f"Found {profile.name} device at {host.ip}:{host.port} with slave ID {slave_id} (Frequency: {frequency} Hz)")
                        return device
                
                device.disconnect()
                
            except Exception as e:
                logger.debug(f"Failed to read {profile.name} at {host.ip}:{host.port} with slave ID {slave_id}: {str(e)}")
                continue
            
            # Add a small delay between slave ID attempts to avoid overwhelming the device
            time.sleep(0.1)
                    
    return None

def read_frequency(device: ModbusTCP, operation: str, start_register: int, num_registers: int, scale_factor: float) -> float:
    """
    Read the frequency value from the device and apply the scale factor.
    """
    try:
        registers = device.read_registers(operation, start_register, num_registers)
        
        if not registers:
            return 0.0
            
        if num_registers == 1:
            # Single register (uint16) - apply scale factor
            return registers[0] * scale_factor
        else:
            # Two registers (float32) - apply scale factor
            return struct.unpack('>f', struct.pack('>HH', registers[0], registers[1]))[0] * scale_factor
            
    except Exception as e:
        logger.debug(f"Error reading frequency: {str(e)}")
        return 0.0