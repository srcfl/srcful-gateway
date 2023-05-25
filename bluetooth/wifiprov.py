#!/usr/bin/env python
import dbus, uuid, sys
import logging
## Change these values
SSID="<SSID>"
PASSWORD="<PASSWORD>"
##

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

def set_ssid_psk(SSID, PASSWORD):

    s_con = dbus.Dictionary({
        'type': '802-11-wireless',
        'uuid': str(uuid.uuid4()),
        'id': SSID,
    })

    s_wifi = dbus.Dictionary({
        'ssid': dbus.ByteArray(bytes(SSID) if sys.version_info < (3, 0) else bytes(SSID, 'utf-8')),
        'mode': 'infrastructure',
        'hidden': dbus.Boolean(True),
    })

    s_wsec = dbus.Dictionary({
        'key-mgmt': 'wpa-psk',
        'auth-alg': 'open',
        'psk': PASSWORD,
    })

    s_ip4 = dbus.Dictionary({'method': 'auto'})
    s_ip6 = dbus.Dictionary({'method': 'auto'})

    con = dbus.Dictionary({
        'connection': s_con,
        '802-11-wireless': s_wifi,
        '802-11-wireless-security': s_wsec,
        'ipv4': s_ip4,
        'ipv6': s_ip6,
    })


    bus = dbus.SystemBus()

    proxy = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager/Settings")
    settings = dbus.Interface(proxy, "org.freedesktop.NetworkManager.Settings")

    print(settings.ListConnections())

    logger.debug(settings.ListConnections())
    
    settings.AddConnection(con)


def remove_connections():

    bus = dbus.SystemBus()

    proxy = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager/Settings")
    settings = dbus.Interface(proxy, "org.freedesktop.NetworkManager.Settings")

    connection_paths = settings.ListConnections()
    logger.debug("Num of connection profiles:", len(connection_paths))
    for path in connection_paths:
        con_proxy = bus.get_object("org.freedesktop.NetworkManager", path)
        settings_connection = dbus.Interface(con_proxy, "org.freedesktop.NetworkManager.Settings.Connection")
        config = settings_connection.GetSettings()
        settings_connection.Delete()