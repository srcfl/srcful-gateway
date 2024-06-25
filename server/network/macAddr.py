import sys


import sys
import dbus
import uuid

class NetworkDeviceNotFoundError(Exception):
    pass

def get_device_mac_address(device_type):
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager'), 'org.freedesktop.NetworkManager')
    for path in manager.GetDevices():
        dev_proxy = bus.get_object('org.freedesktop.NetworkManager', path)
        iface = dbus.Interface(dev_proxy, 'org.freedesktop.DBus.Properties')
        properties = iface.GetAll('org.freedesktop.NetworkManager.Device')
        if properties['DeviceType'] == device_type:
            device_properties = iface.GetAll('org.freedesktop.NetworkManager.Device')
            return device_properties['HwAddress']
    raise NetworkDeviceNotFoundError(f"No device found with DeviceType {device_type}")

def get_eth0():
    if sys.platform == 'linux':
        return get_device_mac_address(1)  # 1 is for ethernet
    else:
        return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])

def get_wlan0():
    if sys.platform == 'linux':
        return get_device_mac_address(2)  # 2 is for wifi
    else:
        raise NotImplementedError("Only implemented for linux platform")
