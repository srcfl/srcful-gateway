import logging
import time
import uuid
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

    def is_connected():
        return True
    
    def get_ip_address():
        return '0.0.0.0'
    
    def get_ip_addresses_with_interfaces():
        return [('No active connection', '0.0.0.0')]

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
            state = dev.Get('org.freedesktop.NetworkManager.Device', 'State', dbus_interface='org.freedesktop.DBus.Properties')
            logger.debug("device state %i", state)
            if state == 100:  # Active connection
                ip_config_objpath = dev.Get('org.freedesktop.NetworkManager.Device', 'Ip4Config', dbus_interface='org.freedesktop.DBus.Properties')
                if ip_config_objpath != '/':  # If there is an associated IP4Config object
                    ip_config_obj = bus.get_object('org.freedesktop.NetworkManager', ip_config_objpath)
                    ip_config_iface = dbus.Interface(ip_config_obj, 'org.freedesktop.NetworkManager.IP4Config')
                    address_data = ip_config_iface.Get('org.freedesktop.NetworkManager.IP4Config', 'AddressData', dbus_interface='org.freedesktop.DBus.Properties')
                    logger.debug("device ip address %s", address_data[0]['address'])
                    if address_data[0]['address'] != '127.0.0.1':
                        return address_data[0]['address']
        logger.info("No active connection found")
        return '0.0.0.0'
    
    def get_connected_ssid() -> str:
         # Connect to system bus
        bus = dbus.SystemBus()
        
        # Get NetworkManager object
        nm = bus.get_object('org.freedesktop.NetworkManager', 
                        '/org/freedesktop/NetworkManager')
        nm_interface = dbus.Interface(nm, 'org.freedesktop.NetworkManager')
        
        # Get all network devices
        devices = nm_interface.GetDevices()
        
        for d in devices:
            dev = bus.get_object('org.freedesktop.NetworkManager', d)
            dev_interface = dbus.Interface(dev, 'org.freedesktop.DBus.Properties')
            
            # Check if device is WiFi
            dev_type = dev_interface.Get('org.freedesktop.NetworkManager.Device', 
                                    'DeviceType')
            if dev_type != 2:  # 2 = WiFi device
                continue
                
            # Check if device is connected
            state = dev_interface.Get('org.freedesktop.NetworkManager.Device', 
                                    'State')
            if state != 100:  # 100 = activated/connected state
                continue
                
            # Get active access point
            active_ap = dev_interface.Get('org.freedesktop.NetworkManager.Device.Wireless',
                                        'ActiveAccessPoint')
            if active_ap == '/':
                continue
                
            # Get AP object and its SSID
            ap = bus.get_object('org.freedesktop.NetworkManager', active_ap)
            ap_props = dbus.Interface(ap, 'org.freedesktop.DBus.Properties')
            ssid = ap_props.Get('org.freedesktop.NetworkManager.AccessPoint', 'Ssid')
            
            # SSID is returned as an array of bytes, convert to string
            return ''.join([chr(b) for b in ssid])
        
        return ""

    def get_ip_addresses_with_interfaces():
        bus = dbus.SystemBus()
        nm_obj = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')
        nm = dbus.Interface(nm_obj, 'org.freedesktop.NetworkManager')
        devices = nm.GetDevices()
        
        ip_addresses = []
        
        for path in devices:
            logger.debug("network device path: %s", path)
            dev_obj = bus.get_object('org.freedesktop.NetworkManager', path)
            dev = dbus.Interface(dev_obj, "org.freedesktop.NetworkManager.Device")
            state = dev.Get('org.freedesktop.NetworkManager.Device', 'State', dbus_interface='org.freedesktop.DBus.Properties')
            iface = dev.Get('org.freedesktop.NetworkManager.Device', 'Interface', dbus_interface='org.freedesktop.DBus.Properties')
            
            logger.debug("device state: %i", state)
            logger.debug("device interface: %s", iface)
            
            if state == 100:  # Active connection
                ip_config_objpath = dev.Get('org.freedesktop.NetworkManager.Device', 'Ip4Config', dbus_interface='org.freedesktop.DBus.Properties')
                if ip_config_objpath != '/':  # If there is an associated IP4Config object
                    ip_config_obj = bus.get_object('org.freedesktop.NetworkManager', ip_config_objpath)
                    ip_config_iface = dbus.Interface(ip_config_obj, 'org.freedesktop.NetworkManager.IP4Config')
                    address_data = ip_config_iface.Get('org.freedesktop.NetworkManager.IP4Config', 'AddressData', dbus_interface='org.freedesktop.DBus.Properties')
                    for address in address_data:
                        if address['address'] != '127.0.0.1':  # Ignore loopback addresses
                            ip_addresses.append((iface, address['address']))
        
        if not ip_addresses:
            logger.debug("No active connection found")
            return []
        
        return ip_addresses

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
            self.bus = dbus.SystemBus()
            
            # Get the NetworkManager object
            self.nm_proxy = self.bus.get_object(
                "org.freedesktop.NetworkManager",
                "/org/freedesktop/NetworkManager"
            )
            self.nm = dbus.Interface(
                self.nm_proxy,
                "org.freedesktop.NetworkManager"
            )
            
            # Get the Settings object
            settings_proxy = self.bus.get_object(
                "org.freedesktop.NetworkManager",
                "/org/freedesktop/NetworkManager/Settings"
            )
            self.settings = dbus.Interface(
                settings_proxy,
                "org.freedesktop.NetworkManager.Settings"
            )
            
            self.ssid = ssid
            self.psk = psk
            self.connection_timeout = 30  # seconds

            # Log existing connections
            self._log_existing_connections()

        def _log_existing_connections(self):
            """Log all existing network connections."""
            for conn in self.settings.ListConnections():
                con_proxy = self.bus.get_object("org.freedesktop.NetworkManager", conn)
                settings_connection = dbus.Interface(
                    con_proxy, "org.freedesktop.NetworkManager.Settings.Connection"
                )
                config = settings_connection.GetSettings()
                logger.info("Connection: %s - %s", conn, config["connection"]["type"])

        def _find_wireless_device(self):
            """Find the first wireless device."""
            devices = self.nm.GetDevices()
            for dev_path in devices:
                dev_proxy = self.bus.get_object("org.freedesktop.NetworkManager", dev_path)
                dev_props = dbus.Interface(dev_proxy, "org.freedesktop.DBus.Properties")
                dev_type = dev_props.Get("org.freedesktop.NetworkManager.Device", "DeviceType")
                if dev_type == 2:  # NM_DEVICE_TYPE_WIFI = 2
                    return dev_path
            return None

        def _add_connection(self, priority=0):
            """Add a new connection profile and return its path. Higher priority (more positive) connections are preferred."""
            s_con = dbus.Dictionary({
                "type": "802-11-wireless",
                "uuid": str(uuid.uuid4()),
                "id": self.ssid,
                "autoconnect": True,
                "autoconnect-priority": dbus.Int32(priority)  # Higher number = higher priority
            })

            s_wifi = dbus.Dictionary({
                "ssid": dbus.ByteArray(
                    bytes(self.ssid) if sys.version_info < (3, 0) else bytes(self.ssid, "utf-8")
                ),
                "mode": "infrastructure",
                "hidden": dbus.Boolean(True),
            })

            s_wsec = dbus.Dictionary({
                "key-mgmt": "wpa-psk",
                "auth-alg": "open",
                "psk": self.psk
            })

            s_ip4 = dbus.Dictionary({"method": "auto"})
            s_ip6 = dbus.Dictionary({"method": "auto"})

            con = dbus.Dictionary({
                "connection": s_con,
                "802-11-wireless": s_wifi,
                "802-11-wireless-security": s_wsec,
                "ipv4": s_ip4,
                "ipv6": s_ip6,
            })

            return self.settings.AddConnection(con)

        def _wait_for_connection_state(self, connection_path, timeout=None):
            """
            Wait for connection to reach a final state (connected or failed).
            Returns True if connected successfully, False if failed.
            """
            if timeout is None:
                timeout = self.connection_timeout

            start_time = time.time()
            while time.time() - start_time < timeout:
                conn_proxy = self.bus.get_object("org.freedesktop.NetworkManager", connection_path)
                conn_props = dbus.Interface(conn_proxy, "org.freedesktop.DBus.Properties")
                
                state = conn_props.Get(
                    "org.freedesktop.NetworkManager.Connection.Active",
                    "State"
                )
                
                # NM_ACTIVE_CONNECTION_STATE_ACTIVATED = 2
                if state == 2:
                    logger.info("Successfully connected to %s", self.ssid)
                    return True
                    
                # NM_ACTIVE_CONNECTION_STATE_DEACTIVATED = 4
                elif state == 4:
                    logger.error("Failed to connect to %s", self.ssid)
                    return False
                    
                time.sleep(0.5)
                
            logger.error("Connection timeout while trying to connect to %s", self.ssid)
            return False

        def _find_existing_connection_by_ssid(self):
            """Find if there's already a connection profile for this SSID."""
            for conn in self.settings.ListConnections():
                con_proxy = self.bus.get_object("org.freedesktop.NetworkManager", conn)
                settings_connection = dbus.Interface(
                    con_proxy, "org.freedesktop.NetworkManager.Settings.Connection"
                )
                config = settings_connection.GetSettings()
                
                # Check if this is a WiFi connection
                if config["connection"]["type"] != "802-11-wireless":
                    continue
                    
                # Get the SSID from the connection settings
                existing_ssid = bytes(config["802-11-wireless"]["ssid"]).decode('utf-8')
                if existing_ssid == self.ssid:
                    return conn
            return None

        def connect(self, priority=0):
            """
            Add and activate the connection with fallback handling.
            Args:
                priority: Connection priority (higher number = higher priority) for autoconnect after reboot
            Returns True if connected successfully, False otherwise.
            """
            try:
                # Check if we already have a connection for this SSID
                existing_conn = self._find_existing_connection_by_ssid()
                if existing_conn:
                    logger.info("Found existing connection for SSID: %s. Will activate it.", self.ssid)
                    device_path = self._find_wireless_device()
                    if not device_path:
                        raise Exception("No wireless device found")
                        
                    active_path = self.nm.ActivateConnection(
                        existing_conn,
                        device_path,
                        "/"
                    )
                    return self._wait_for_connection_state(active_path)

                # If no existing connection, proceed with creating new one
                logger.info("No existing connection found. Adding and activating new connection to %s...", self.ssid)
                connection_path = self._add_connection(priority)
                
                try:
                    device_path = self._find_wireless_device()
                    if not device_path:
                        raise Exception("No wireless device found")

                    active_path = self.nm.ActivateConnection(
                        connection_path,
                        device_path,
                        "/"
                    )
                    
                    # Wait for connection to succeed or fail
                    if not self._wait_for_connection_state(active_path):
                        logger.warning("Connection failed, cleaning up connection profile")
                        # Clean up the failed connection profile
                        self.delete_connection(connection_path)
                        return False

                    return True

                except Exception as e:
                    logger.error("Failed to activate connection: %s", str(e))
                    # Clean up the connection profile if activation failed
                    self.delete_connection(connection_path)
                    return False

            except Exception as e:
                logger.error("Failed to connect: %s", str(e))
                return False

        def delete_connection(self, connection_path):
            """Delete a specific connection profile."""
            try:
                con_proxy = self.bus.get_object("org.freedesktop.NetworkManager", connection_path)
                settings_connection = dbus.Interface(
                    con_proxy, "org.freedesktop.NetworkManager.Settings.Connection"
                )
                settings_connection.Delete()
                logger.debug("Deleted connection profile: %s", connection_path)
            except Exception as e:
                logger.error("Failed to delete connection: %s", str(e))

        def delete_connections(self):
            """Delete all WiFi connections."""
            logger.info("Deleting all wifi connections...")
            connection_paths = self.settings.ListConnections()
            logger.debug("Num of connection profiles: %i", len(connection_paths))
            
            for path in connection_paths:
                con_proxy = self.bus.get_object("org.freedesktop.NetworkManager", path)
                settings_connection = dbus.Interface(
                    con_proxy, "org.freedesktop.NetworkManager.Settings.Connection"
                )
                config = settings_connection.GetSettings()
                if config["connection"]["type"] == "802-11-wireless":
                    settings_connection.Delete()
                    logger.debug("Deleted connection profile: %s", config["connection"]["id"])

            logger.debug("Deleted all wifi connection profiles...")