import logging
import uuid, sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

try:
  import dbus
except ImportError:
  logger.info("dbus not found - possibly on non linux platform")
  logger.info("wifi provisioning will not work")

  class WiFiHandler:
    def __init__(self, SSID, PSK):
      pass
    def _AddConnection(self):
      pass
    def _DeleteConnections(self):
      pass
    def connect(self):
      pass

else:
  class WiFiHandler:

    def __init__(self, SSID, PSK):
      self.bus = dbus.SystemBus() # Is this needed as a field? 
      proxy = self.bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager/Settings")
      self.settings = dbus.Interface(proxy, "org.freedesktop.NetworkManager.Settings")
      self.SSID = SSID
      self.PSK = PSK


    def _AddConnection(self):

      s_con = dbus.Dictionary({
      'type': '802-11-wireless',
      'uuid': str(uuid.uuid4()),
      'id': self.SSID,
      })

      s_wifi = dbus.Dictionary({
        'ssid': dbus.ByteArray(bytes(SSID) if sys.version_info < (3, 0) else bytes(self.SSID, 'utf-8')),
        'mode': 'infrastructure',
        'hidden': dbus.Boolean(True)})

      s_wsec = dbus.Dictionary({
        'key-mgmt': 'wpa-psk',
        'auth-alg': 'open',
        'psk': self.PSK})

      s_ip4 = dbus.Dictionary({'method': 'auto'})
      s_ip6 = dbus.Dictionary({'method': 'auto'})

      con = dbus.Dictionary({
        'connection': s_con,
        '802-11-wireless': s_wifi,
        '802-11-wireless-security': s_wsec,
        'ipv4': s_ip4,
        'ipv6': s_ip6})

      self.settings.AddConnection(con)


    def _DeleteConnections(self):
      connection_paths = self.settings.ListConnections()
      logger.debug("Num of connection profiles:", len(connection_paths))
      for path in connection_paths:
        con_proxy = self.bus.get_object("org.freedesktop.NetworkManager", path)
        settings_connection = dbus.Interface(con_proxy, "org.freedesktop.NetworkManager.Settings.Connection")
        config = settings_connection.GetSettings()
        settings_connection.Delete()
      
      logger.debug("Deleted all connection profiles...")


    def connect(self):
      self._DeleteConnections()
      self._AddConnection()