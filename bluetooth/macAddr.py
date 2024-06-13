import sys


def get():
    if sys.platform == 'linux':
        try:
            return open('/sys/class/net/eth0/address').readline().strip().upper()
        except FileNotFoundError:
            return "FF:FF:FF:FF:FF:FF"
    else:
        import uuid
        return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])


def get_wifi_mac():
    if sys.platform != 'linux':
        import dbus
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager'), 'org.freedesktop.NetworkManager')
        for path in manager.GetDevices():
            dev_proxy = bus.get_object('org.freedesktop.NetworkManager', path)
            iface = dbus.Interface(dev_proxy, 'org.freedesktop.DBus.Properties')
            properties = iface.GetAll('org.freedesktop.NetworkManager.Device')
            if properties['DeviceType'] == 2:  # 2 is for wifi
                wifi_iface = dbus.Interface(dev_proxy, 'org.freedesktop.NetworkManager.Device.Wireless')
                wifi_properties = iface.GetAll('org.freedesktop.NetworkManager.Device.Wireless')
                return wifi_properties['HwAddress']
    else:
        raise NotImplementedError("Only implemented for linux platform")