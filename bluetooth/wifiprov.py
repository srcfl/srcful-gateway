#!/usr/bin/env python
import logging, uuid, sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name=__name__)

try:
  import dbus
except ImportError:
  logger.info("dbus not found - possibly on non linux platform")
  logger.info("wifi provisioning will not work")

  def set_ssid_psk(SSID, PASSWORD):
    pass
  def remove_connections():
    pass

else:
  # we have dbus
  ## Change these values
  SSID="<SSID>"
  PASSWORD="<PASSWORD>"
  ##

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

      logger.debug(settings.ListConnections())

      logger.debug(settings.ListConnections())
      
      settings.AddConnection(con)


  def remove_connections():

      bus = dbus.SystemBus()

      proxy = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager/Settings")
      settings = dbus.Interface(proxy, "org.freedesktop.NetworkManager.Settings")

      connection_paths = settings.ListConnections()
      logger.debug("Num of connection profiles: %d", len(connection_paths))
      for path in connection_paths:
          con_proxy = bus.get_object("org.freedesktop.NetworkManager", path)
          settings_connection = dbus.Interface(con_proxy, "org.freedesktop.NetworkManager.Settings.Connection")
          config = settings_connection.GetSettings()
          settings_connection.Delete()