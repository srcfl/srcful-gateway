import logging
import uuid
import sys

logger = logging.getLogger(__name__)

try:
    import dbus
except ImportError:
    logger.info("dbus not found - possibly on non linux platform")
    logger.info("wifi provisioning will not work")

    def get_connection_configs():
        config = {"connection": {"type": "802-11-wireless"}}
        return [config]

    class WiFiHandler:
        def __init__(self, ssid, psk):
            pass

        def _add_connection(self):
            pass

        def _delete_connections(self):
            pass

        def connect(self):
            pass

else:

    def is_connected():
        bus = dbus.SystemBus()
        nm_obj = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')
        state = nm_obj.Get('org.freedesktop.NetworkManager', 'State', dbus_interface='org.freedesktop.DBus.Properties')
        return state == 70  # 70 corresponds to "connected globally"
    
    def get_ip_address():
        bus = dbus.SystemBus()
        nm_obj = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')
        nm = dbus.Interface(nm_obj, 'org.freedesktop.NetworkManager')
        devices = nm.GetDevices()
        for path in devices:
            logger.debug("network device path: %s", path)
            dev_obj = bus.get_object('org.freedesktop.NetworkManager', path)
            dev = dbus.Interface(dev_obj, "org.freedesktop.NetworkManager.Device")
            logger.debug("network device %s", dev)
            if dev.State == 100:  # Active connection
                ip_obj = bus.get_object('org.freedesktop.NetworkManager', dev.Ip4Config)
                ip = dbus.Interface(ip_obj, 'org.freedesktop.NetworkManager.IP4Config')
                logger.debug("device ip address: %s", ip.AddressData[0]['address'])
                if ip.AddressData[0]['address'] != '127.0.0.1':
                    return ip.AddressData[0]['address']
        logger.debug("No active connection found")
        return '0.0.0.0'

    def get_connection_configs():
        bus = dbus.SystemBus()
        proxy = bus.get_object(
            "org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager/Settings"
        )
        settings = dbus.Interface(proxy, "org.freedesktop.NetworkManager.Settings")
        ret = []
        for conn in settings.ListConnections():
            con_proxy = bus.get_object("org.freedesktop.NetworkManager", conn)
            settings_connection = dbus.Interface(
                con_proxy, "org.freedesktop.NetworkManager.Settings.Connection"
            )
            config = settings_connection.GetSettings()
            ret.append(config)
        return ret

    class WiFiHandler:
        def __init__(self, ssid, psk):
            logger.info("WiFiHandler init with SSID: %s", ssid)
            self.bus = dbus.SystemBus()  # Is this needed as a field?
            proxy = self.bus.get_object(
                "org.freedesktop.NetworkManager",
                "/org/freedesktop/NetworkManager/Settings",
            )
            self.settings = dbus.Interface(
                proxy, "org.freedesktop.NetworkManager.Settings"
            )
            self.ssid = ssid
            self.psk = psk

            connection_paths = self.settings.ListConnections()
            logger.debug("Num of connection profiles: %i", len(connection_paths))

            # lets just log all connections
            for conn in self.settings.ListConnections():
                con_proxy = self.bus.get_object("org.freedesktop.NetworkManager", conn)
                settings_connection = dbus.Interface(
                    con_proxy, "org.freedesktop.NetworkManager.Settings.Connection"
                )
                config = settings_connection.GetSettings()
                logger.info("Connection: %s - %s", conn, config["connection"]["type"])

        def _add_connection(self):
            s_con = dbus.Dictionary(
                {
                    "type": "802-11-wireless",
                    "uuid": str(uuid.uuid4()),
                    "id": self.ssid,
                }
            )

            s_wifi = dbus.Dictionary(
                {
                    "ssid": dbus.ByteArray(
                        bytes(self.ssid)
                        if sys.version_info < (3, 0)
                        else bytes(self.ssid, "utf-8")
                    ),
                    "mode": "infrastructure",
                    "hidden": dbus.Boolean(True),
                }
            )

            s_wsec = dbus.Dictionary(
                {"key-mgmt": "wpa-psk", "auth-alg": "open", "psk": self.psk}
            )

            s_ip4 = dbus.Dictionary({"method": "auto"})
            s_ip6 = dbus.Dictionary({"method": "auto"})

            con = dbus.Dictionary(
                {
                    "connection": s_con,
                    "802-11-wireless": s_wifi,
                    "802-11-wireless-security": s_wsec,
                    "ipv4": s_ip4,
                    "ipv6": s_ip6,
                }
            )

            self.settings.AddConnection(con)

        def _delete_connections(self):
            connection_paths = self.settings.ListConnections()
            logger.debug("Num of connection profiles: %i", len(connection_paths))
            for path in connection_paths:
                con_proxy = self.bus.get_object("org.freedesktop.NetworkManager", path)
                settings_connection = dbus.Interface(
                    con_proxy, "org.freedesktop.NetworkManager.Settings.Connection"
                )
                config = settings_connection.GetSettings()
                # only delete wifi connections
                if config["connection"]["type"] == "802-11-wireless":
                    settings_connection.Delete()
                    logger.debug("Deleted connection profile: %s", config["connection"]["id"])

            logger.debug("Deleted all wifi connection profiles...")

        def connect(self):
            logger.info("Deleting connections...")
            self._delete_connections()
            logger.info("Adding connection...")
            self._add_connection()
