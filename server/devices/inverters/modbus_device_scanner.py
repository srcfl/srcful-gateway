from typing import List, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from server.network.network_utils import HostInfo, NetworkUtils
from server.devices.ICom import ICom
from server.devices.supported_devices.profiles import ModbusProfile, ModbusDeviceProfiles
from server.devices.profile_keys import ProtocolKey, ProfileKey
from server.devices.inverters.ModbusTCP import ModbusTCP
import time
from datetime import datetime
from server.network.mac_lookup import MacLookupService
from threading import Lock


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

_scan_lock = Lock()
_is_scanning = False

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

def is_scanning() -> bool:
    global _is_scanning
    return _is_scanning

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
    
    # log what we got from the argument
    logger.debug(f"Got manufacturer: {manufacturer}")
    
    if not manufacturer:
        return profiles
        
    matching_profiles = []
    
    # Get matching profiles based on standardized manufacturer name
    for profile in profiles:
        
        # manufacturer name could for example be HUAWEI TECHNOLOGIES CO.,LTD
        keywords = [profile.name.lower(), profile.display_name.lower()]
            
        # Add any additional keywords from profile
        if hasattr(profile, ProfileKey.KEYWORDS):
            keywords.extend([k.lower() for k in profile.keywords])
            
        # logger.debug(f"The following keywords are available for {profile.name}: {keywords}")
        
            
        if any(keyword in manufacturer.lower() for keyword in keywords):
            logger.debug(f"Found matching profile: {profile.name}, name was in {manufacturer}")
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
    
    if host.port == 8899:
        return None  # Solarman devices need dongle serial number

    
    manufacturer = MacLookupService.get_manufacturer(host.mac)
    profiles = get_profile_by_manufacturer(manufacturer, all_profiles)
    
    logger.debug(f"The following profiles are available for {host.mac}: {[profile.name for profile in profiles]}")
    
    # Test manufacturer-specific profiles
    for profile in profiles:
        device = try_profile(host, profile)
        if device:
            return device
    
    return None

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
                return device
            
            device.disconnect()
            
        except Exception:
            continue
        
        time.sleep(0.5)
    
    return None


def filter_open_devices(hosts: List[HostInfo], open_devices: List[ICom]) -> List[HostInfo]:
    open_devices_hostinfo: List[HostInfo] = []
    
    for open_device in open_devices:
        if isinstance(open_device, ModbusTCP):
            open_device_hostinfo = HostInfo(
                ip=open_device.ip,
                port=open_device.port,
                mac=open_device.mac
            )

            open_devices_hostinfo.append(open_device_hostinfo)
            
    def compare_hostinfo(host: HostInfo, open_device_hostinfo: HostInfo) -> bool:   
        return host.ip == open_device_hostinfo.ip and host.port == open_device_hostinfo.port and host.mac == open_device_hostinfo.mac
            
    filtered_hostinfos = [host for host in hosts if not any(compare_hostinfo(host, open_device_hostinfo) for open_device_hostinfo in open_devices_hostinfo)]
            
    return filtered_hostinfos
    

@log_execution_time
def scan_for_modbus_devices(ports: List[int], timeout: float = NetworkUtils.DEFAULT_TIMEOUT, open_devices: List[ICom] = []) -> List[ICom]:
    """
    Scan the network for Modbus TCP devices and try to identify their make/model.
    Returns empty list if a scan is already in progress.
    """
    global _is_scanning
    
    if not _scan_lock.acquire(blocking=False):
        logger.warning("A Modbus device scan is already in progress. Skipping this request.")
        return []
        
    try:
        _is_scanning = True
        scan_start_time = time.time()
        
        # Get all available profiles
        all_profiles = [p for p in ModbusDeviceProfiles().get_supported_devices() 
                       if p.protocol == ProtocolKey.MODBUS and 
                       p.registers and 
                       p.name != "unknown"]
        
        devices: List[ICom] = []
        
        # Scan network
        network_scan_start = time.time()
        hosts = NetworkUtils.get_hosts(ports=ports, timeout=timeout)
        network_scan_elapsed = time.time() - network_scan_start
        
        if not hosts:
            logger.info("No hosts found with open Modbus ports")
            return devices

        # Filter out already open devices
        filtered_hostinfos = filter_open_devices(hosts, open_devices)
        
        if len(filtered_hostinfos) == 0:
            logger.info("No new hosts found that are not already open")
            return devices

        # Device identification phase
        identification_start = time.time()
        with ThreadPoolExecutor(max_workers=min(32, len(filtered_hostinfos))) as executor:
            future_to_host = {
                executor.submit(identify_device, hostinfo, all_profiles): hostinfo
                for hostinfo in filtered_hostinfos
            }
            
            for future in as_completed(future_to_host):
                host = future_to_host[future]
                try:
                    device = future.result()
                    if device:
                        devices.append(device)
                except Exception:
                    pass
        
        total_elapsed = time.time() - scan_start_time
        
        # Log compact summary
        logger.info("=" * 50)
        logger.info("Modbus Scan Results:")
        logger.info(f"- Scan time: {total_elapsed:.1f}s")
        logger.info(f"- Hosts scanned: {len(filtered_hostinfos)}")
        logger.info(f"- Devices found: {len(devices)}")
        if devices:
            for device in devices:
                logger.info(f"  * {device.get_config()}")
        logger.info("=" * 50)

        return devices

    finally:
        _is_scanning = False
        _scan_lock.release()

