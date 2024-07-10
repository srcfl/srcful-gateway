import sys
import uuid
import logging

logger = logging.getLogger(__name__)

try:
    import dbus
except ImportError:
    logger.info("dbus not found - possibly on non linux platform")
    logger.info("wifi provisioning will not work")
else:
    class NetworkDeviceNotFoundError(Exception):
        pass

    class IPAddressNotFoundError(Exception):
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
        

    def get_eth0_ip():
        if sys.platform == 'linux':
            return get_ip_address_for_interface(1)  # 1 is for ethernet
        else:
            return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])

    def get_wlan0_ip():
        if sys.platform == 'linux':
            return get_ip_address_for_interface(2)  # 2 is for wifi
        else:
            raise NotImplementedError("Only implemented for linux platform")
        
    def get_ip_address_for_interface(device_type):
        
        bus = dbus.SystemBus()
        nm_obj = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')
        nm = dbus.Interface(nm_obj, 'org.freedesktop.NetworkManager')
        devices = nm.GetDevices()

        for path in devices:
            logger.debug("Hello World!")
            dev_obj = bus.get_object('org.freedesktop.NetworkManager', path)
            dev_iface = dbus.Interface(dev_obj, "org.freedesktop.NetworkManager.Device")
            iface = dev_iface.Get('org.freedesktop.NetworkManager.Device', 'Interface', dbus_interface='org.freedesktop.DBus.Properties')

            properties = iface.GetAll('org.freedesktop.NetworkManager.Device')
            logger.debug("interface %s", iface)
            logger.debug("properties", properties)
            if properties['DeviceType'] == device_type:
                logger.debug("Found something")
                state = dev_iface.Get('org.freedesktop.NetworkManager.Device', 'State', dbus_interface='org.freedesktop.DBus.Properties')
                if state == 100:  # Active connection
                    ip_config_objpath = dev_iface.Get('org.freedesktop.NetworkManager.Device', 'Ip4Config', dbus_interface='org.freedesktop.DBus.Properties')
                    if ip_config_objpath != '/':  # If there is an associated IP4Config object
                        ip_config_obj = bus.get_object('org.freedesktop.NetworkManager', ip_config_objpath)
                        ip_config_iface = dbus.Interface(ip_config_obj, 'org.freedesktop.NetworkManager.IP4Config')
                        address_data = ip_config_iface.Get('org.freedesktop.NetworkManager.IP4Config', 'AddressData', dbus_interface='org.freedesktop.DBus.Properties')
                        for address in address_data:
                            if address['address'] != '127.0.0.1':  # Ignore loopback addresses
                                return address['address']
        raise IPAddressNotFoundError(f"Ip address for interface {device_type} not found.")
