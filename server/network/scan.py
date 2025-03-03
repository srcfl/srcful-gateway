import logging

from server.network import wifi

logger = logging.getLogger(__name__)

try:
    import dbus
except ImportError:
    logger.info("dbus not found - possibly on non linux platform")
    logger.info("wifi provisioning will not work")

    def get_connection_configs():
        config = {"connection": {"type": "802-11-wireless"}}
        return [config]

    class WifiScanner:
        def __init__(self):
            self.ssids = ["test1", "test2"]

        def scan(self):
            pass

        def get_ssids(self):
            return self.ssids

        def get_connected_ssid(self):
            return "Unknown"

else:

    class WifiScanner:
        def __init__(self):
            # property will not be set until 3 to 5 seconds after the scan is started
            self.ssids = []

        def get_connected_ssid(self):
            return wifi.get_connected_ssid()

        def get_ssids(self):
            if len(self.ssids) == 0:
                bus = dbus.SystemBus()

                # Get a proxy for the base NetworkManager object
                proxy = bus.get_object(
                    "org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager"
                )
                manager = dbus.Interface(proxy, "org.freedesktop.NetworkManager")

                # Get all network devices
                devices = manager.GetDevices()
                for d in devices:
                    dev_proxy = bus.get_object("org.freedesktop.NetworkManager", d)
                    prop_iface = dbus.Interface(
                        dev_proxy, "org.freedesktop.DBus.Properties"
                    )

                    # Make sure the device is enabled before we try to use it
                    state = prop_iface.Get(
                        "org.freedesktop.NetworkManager.Device", "State"
                    )
                    if state <= 2:
                        continue

                    # Get device's type; we only want wifi devices
                    dtype = prop_iface.Get(
                        "org.freedesktop.NetworkManager.Device", "DeviceType"
                    )
                    if dtype == 2:  # WiFi
                        # Get a proxy for the wifi interface
                        wifi_iface = dbus.Interface(
                            dev_proxy, "org.freedesktop.NetworkManager.Device.Wireless"
                        )

                        aps = wifi_iface.GetAllAccessPoints()

                        for path in aps:
                            try:
                                ap_proxy = bus.get_object(
                                    "org.freedesktop.NetworkManager", path
                                )
                                ap_prop_iface = dbus.Interface(
                                    ap_proxy, "org.freedesktop.DBus.Properties"
                                )

                                ssid = bytearray(
                                    ap_prop_iface.Get(
                                        "org.freedesktop.NetworkManager.AccessPoint", "Ssid"
                                    )
                                ).decode()

                                # Cache the BSSID
                                if ssid not in self.ssids:
                                    self.ssids.append(ssid)

                            except Exception as e:
                                logger.error("Failed to get SSID for access point %s", path)
                                logger.exception(e)

            return self.ssids

        def scan(self):
            self.ssids = []
            bus = dbus.SystemBus()

            # Get a proxy for the base NetworkManager object
            proxy = bus.get_object(
                "org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager"
            )
            manager = dbus.Interface(proxy, "org.freedesktop.NetworkManager")

            # Get all network devices
            devices = manager.GetDevices()
            for d in devices:
                dev_proxy = bus.get_object("org.freedesktop.NetworkManager", d)
                prop_iface = dbus.Interface(
                    dev_proxy, "org.freedesktop.DBus.Properties"
                )

                # Make sure the device is enabled before we try to use it
                state = prop_iface.Get("org.freedesktop.NetworkManager.Device", "State")
                if state <= 2:
                    continue

                # Get device's type; we only want wifi devices
                dtype = prop_iface.Get(
                    "org.freedesktop.NetworkManager.Device", "DeviceType"
                )
                if dtype == 2:  # WiFi
                    # Get a proxy for the wifi interface
                    wifi_iface = dbus.Interface(
                        dev_proxy, "org.freedesktop.NetworkManager.Device.Wireless"
                    )

                    opt = dbus.Dictionary({})
                    # Get all APs the card can see
                    wifi_iface.RequestScan(opt)