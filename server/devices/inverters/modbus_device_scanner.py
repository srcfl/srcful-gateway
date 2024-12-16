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
from server.network.mac_lookup import MacLookupService


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

"""
1. Get all supported Modbus/Solarman profiles
2. Scan the network for hosts with open Modbus ports
3. For each host in parallel:
   - Look up manufacturer from MAC address
   - If manufacturer found, test matching profiles
   - If no manufacturer or no match, return as unknown device
4. Return list of all found devices

scan_for_modbus_devices()  # Entry point
│
├─── Get all Modbus/Solarman profiles
│
├─── Network scan for open ports
│
├─── ThreadPoolExecutor (max_workers=32)
│    │
│    ├─── Host1 Thread [identify_device()]
│    │    ├─── MAC lookup -> Get manufacturer
│    │    ├─── Filter profiles by manufacturer
│    │    └─── Test matching profiles
│    │        ├─── Try Slave IDs 0-5
│    │        └─── Return first working device or unknown
│    │
│    ├─── Host2 Thread [identify_device()]
│    │    ├─── MAC lookup -> Get manufacturer
│    │    ├─── Filter profiles by manufacturer
│    │    └─── Test matching profiles
│    │        ├─── Try Slave IDs 0-5
│    │        └─── Return first working device or unknown
│    │
│    └─── Host3 Thread [identify_device()]
│         ├─── MAC lookup -> Get manufacturer
│         ├─── Filter profiles by manufacturer
│         └─── Test matching profiles
│             ├─── Try Slave IDs 0-5
│             └─── Return first working device or unknown
│
└─── Main Thread
     └─── Collect results and return device list
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

def get_profile_by_manufacturer(manufacturer: str, profiles: List[ModbusProfile]) -> List[ModbusProfile]:
    """
    Return matching profiles based on manufacturer name, 
    or return all profiles if no manufacturer is found
    """
    if not manufacturer:
        return profiles
        
    matching_profiles = []
    
    # Get matching profiles based on standardized manufacturer name
    for profile in profiles:
        
        # manufacturer name could for example be HUAWEI TECHNOLOGIES CO.,LTD
        # and the profile name could be huawei, so we simply can check if 
        # the manufacturer name contains the profile name
        if profile.name.lower() in manufacturer.lower():
            matching_profiles.append(profile)
    
    return matching_profiles if matching_profiles else profiles

def create_unknown_device(host: HostInfo) -> ICom:
    """
    Create a device object for an unknown/unidentified device
    """
    logger.debug(f"[{get_timestamp()}] Creating unknown device for {host.ip}:{host.port}")
    return ModbusTCP(
        ip=host.ip,
        port=host.port,
        mac=host.mac,
        slave_id=None,
        device_type="Unknown"
    )

@log_execution_time
def identify_device(host: HostInfo, all_profiles: List[ModbusProfile]) -> Optional[ICom]:
    """
    Try to identify a device by first checking MAC manufacturer.
    Returns unknown device if no match found.
    """
    start_time = time.time()
    logger.debug(f"[{get_timestamp()}] Starting device identification for {host.ip}:{host.port}")
    
    # Lookup manufacturer and get matching profiles
    manufacturer = MacLookupService.get_manufacturer(host.mac)
    if manufacturer:
        logger.debug(f"[{get_timestamp()}] Found manufacturer for {host.mac}: {manufacturer}")
        profiles = get_profile_by_manufacturer(manufacturer, all_profiles)
        logger.debug(f"[{get_timestamp()}] Testing {len(profiles)} matching profiles for {manufacturer}")
        
        # Test manufacturer-specific profiles
        for profile in profiles:
            device = try_profile(host, profile)
            if device:
                elapsed = time.time() - start_time
                logger.debug(f"[{get_timestamp()}] Device identification completed in {elapsed:.2f}s")
                return device
    
    # If no manufacturer found or no matching device, create unknown device
    elapsed = time.time() - start_time
    logger.debug(f"[{get_timestamp()}] Device identification completed in {elapsed:.2f}s")
    return create_unknown_device(host)

def try_profile(host: HostInfo, profile: ModbusProfile) -> Optional[ICom]:
    """Helper function to try a specific profile with different slave IDs"""
    for slave_id in range(6):
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
                           f"with slave ID {slave_id} (freq: {device._read_frequency():.2f} Hz)")
                return device
            
            device.disconnect()
            
        except Exception as e:
            logger.debug(f"[{get_timestamp()}] Failed to read {profile.name} at {host.ip}:{host.port} "
                       f"with slave ID {slave_id}: {str(e)}")
            continue
        
        time.sleep(0.5)
    
    return None

@log_execution_time
def scan_for_modbus_devices(ports: List[int], timeout: float = NetworkUtils.DEFAULT_TIMEOUT) -> List[ICom]:
    """
    Scan the network for Modbus TCP devices and try to identify their make/model
    by reading the frequency register.
    """
    scan_start_time = time.time()
    logger.info(f"[{get_timestamp()}] Starting Modbus device scan")
    
    # Get all available profiles once
    all_profiles = [p for p in ModbusDeviceProfiles().get_supported_devices() 
                   if p.protocol == ProtocolKey.MODBUS or ProtocolKey.SOLARMAN and p.registers]
    
    devices: List[ICom] = []
    
    # Scan network for hosts with open Modbus ports
    network_scan_start = time.time()
    hosts = NetworkUtils.get_hosts(ports=ports, timeout=timeout)
    network_scan_elapsed = time.time() - network_scan_start
    
    if not hosts:
        logger.info(f"[{get_timestamp()}] No hosts found with open Modbus ports "
                   f"[Network scan took: {network_scan_elapsed:.2f}s]")
        return devices

    total_hosts = len(hosts)
    total_profiles = len(all_profiles)
    slave_ids = 6
    total_combinations = total_hosts * total_profiles * slave_ids
    host_array = [(host.ip, host.port, host.mac) for host in hosts]
    
    # Log initial summary
    logger.info("=" * 80)
    logger.info(f"[{get_timestamp()}] Modbus Scan Summary (Start):")
    logger.info(f"Network scan completed in {network_scan_elapsed:.2f}s")
    logger.info(f"- Found {total_hosts} host{'s' if total_hosts != 1 else ''} with open Modbus ports")
    logger.info(f"Hosts: {host_array}")
    logger.info(f"- Testing {total_profiles} device profile{'s' if total_profiles != 1 else ''}")
    logger.info(f"- Testing slave IDs 0-5 for each combination")
    logger.info(f"- Total combinations to test: {total_combinations}")
    logger.info(f"- Estimated time: {(total_combinations * 0.5):.1f}s (0.5s per test)")
    logger.info("=" * 80)

    # Device identification phase
    identification_start = time.time()
    with ThreadPoolExecutor(max_workers=min(32, len(hosts))) as executor:
        future_to_host = {
            executor.submit(identify_device, host, all_profiles): host 
            for host in hosts
        }
        
        for future in as_completed(future_to_host):
            host = future_to_host[future]
            try:
                device = future.result()
                if device:
                    devices.append(device)
            except Exception as e:
                logger.debug(f"Failed to process host {host.ip}: {str(e)}")
    
    identification_elapsed = time.time() - identification_start
    total_elapsed = time.time() - scan_start_time
    
    # Log final summary
    logger.info("=" * 80)
    logger.info(f"[{get_timestamp()}] Modbus Scan Complete:")
    logger.info(f"Total scan time: {total_elapsed:.2f}s")
    logger.info(f"- Network scan: {network_scan_elapsed:.2f}s")
    logger.info(f"- Device identification: {identification_elapsed:.2f}s")
    logger.info(f"- Average time per host: {(identification_elapsed/total_hosts):.2f}s")
    logger.info(f"Found {len(devices)} device{'s' if len(devices) != 1 else ''}:")
    if devices:
        for device in devices:
            logger.info(f"- {device.device_type} at {device.ip}:{device.port} (Slave ID: {device.slave_id})")
    else:
        logger.info("No devices found")
    logger.info("=" * 80)

    return devices

