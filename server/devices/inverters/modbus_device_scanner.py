from typing import List, Optional
import struct
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from server.network.network_utils import HostInfo, NetworkUtils
from server.devices.ICom import ICom
from server.devices.supported_devices.profiles import ModbusProfile, ModbusDeviceProfiles
from server.devices.profile_keys import ProtocolKey
from server.devices.inverters.ModbusTCP import ModbusTCP
import time
from datetime import datetime


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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

# Add timing decorator for detailed function timing
def log_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.debug(f"{func.__name__} took {elapsed_time:.2f} seconds to execute")
        return result
    return wrapper

def get_timestamp():
    """Return current timestamp in ISO format"""
    return datetime.now().isoformat()


@log_execution_time
def identify_device(host: HostInfo) -> Optional[ICom]:
    """
    Try to identify a device by testing profiles sequentially, then slave IDs sequentially.
    This function runs in parallel for different hosts.
    """
    start_time = time.time()    
    profiles: List[ModbusProfile] = ModbusDeviceProfiles().get_supported_devices()
    
    # Test each profile sequentially
    for profile in profiles:
        profile_start = time.time()
        
        if profile.protocol != ProtocolKey.MODBUS or not profile.registers:
            continue
        
        # Test each slave ID sequentially for this profile
        for slave_id in range(6):
            slave_start = time.time()
            try:
                device = ModbusTCP(
                    ip=host.ip,
                    port=host.port,
                    mac=host.mac,
                    slave_id=slave_id,
                    device_type=profile.name
                )
                
                if device.connect():
                    logger.debug(f"[{get_timestamp()}] Found {profile.name} device at {host.ip}:{host.port} "
                                  f"with slave ID {slave_id} (freq: {device._read_frequency():.2f} Hz). Elapsed: {time.time() - start_time:.2f}s")
                    return device
                
                device.disconnect()
                
            except Exception as e:
                slave_elapsed = time.time() - slave_start
                logger.debug(f"[{get_timestamp()}] Failed to read {profile.name} at {host.ip}:{host.port} "
                           f"with slave ID {slave_id}: {str(e)} [Took: {slave_elapsed:.2f}s]")
                continue
            
            time.sleep(0.5)
        
        profile_elapsed = time.time() - profile_start
        
        logger.debug(f"[{get_timestamp()}] Completed testing profile {profile.name} and no device found "
                    f"[Took: {profile_elapsed:.2f}s] for {host.ip}:{host.port}, {host.mac}")
                    
    total_elapsed = time.time() - start_time
    logger.debug(f"[{get_timestamp()}] Completed device identification for {host.ip}:{host.port} "
                f"[Total time: {total_elapsed:.2f}s]")
    return None


@log_execution_time
def scan_for_modbus_devices(ports: List[int], timeout: float = NetworkUtils.DEFAULT_TIMEOUT) -> List[ICom]:
    """
    Scan the network for Modbus TCP devices and try to identify their make/model
    by reading the frequency register.
    """
    scan_start_time = time.time()
    logger.debug(f"[{get_timestamp()}] Starting Modbus device scan")
    
    devices: List[ICom] = []
    
    # Scan network for hosts with open Modbus ports
    network_scan_start = time.time()
    hosts = NetworkUtils.get_hosts(ports=ports, timeout=timeout)
    network_scan_elapsed = time.time() - network_scan_start
    
    if not hosts:
        logger.debug(f"[{get_timestamp()}] No hosts found with open Modbus ports "
                    f"[Network scan took: {network_scan_elapsed:.2f}s]")
        return devices

    profiles = [p for p in ModbusDeviceProfiles().get_supported_devices() 
               if p.protocol == ProtocolKey.MODBUS and p.registers]
    
    total_hosts = len(hosts)
    total_profiles = len(profiles)
    slave_ids = 6
    total_combinations = total_hosts * total_profiles * slave_ids
    host_array = [(host.ip, host.port, host.mac) for host in hosts]
    
    # Log initial summary
    logger.debug("=" * 80)
    logger.debug(f"[{get_timestamp()}] Modbus Scan Summary:")
    logger.debug(f"Network scan completed in {network_scan_elapsed:.2f}s")
    logger.debug(f"- Found {total_hosts} host{'s' if total_hosts != 1 else ''} with open Modbus ports")
    logger.debug(f"Hosts: {host_array}")
    logger.debug(f"- Testing {total_profiles} device profile{'s' if total_profiles != 1 else ''}")
    logger.debug(f"- Testing slave IDs 0-5 for each combination")
    logger.debug(f"- Total combinations to test: {total_combinations}")
    logger.debug("=" * 80)

    # Device identification phase
    identification_start = time.time()
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
                pass
    
    identification_elapsed = time.time() - identification_start
    total_elapsed = time.time() - scan_start_time
    
    # Log final summary
    logger.debug("=" * 80)
    logger.debug(f"[{get_timestamp()}] Modbus Scan Complete:")
    logger.debug(f"Total scan time: {total_elapsed:.2f}s")
    logger.debug(f"- Network scan: {network_scan_elapsed:.2f}s")
    logger.debug(f"- Device identification: {identification_elapsed:.2f}s")
    logger.debug(f"Found {len(devices)} device{'s' if len(devices) != 1 else ''}:")
    if devices:
        for device in devices:
            logger.debug(f"- {device.device_type} at {device.ip}:{device.port} (Slave ID: {device.slave_id})")
    else:
        logger.debug("No devices found")
    logger.debug("=" * 80)
                
    return devices

