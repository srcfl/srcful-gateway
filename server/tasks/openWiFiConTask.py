from .task import Task
from server.wifi.wifi import WiFiHandler

import logging
log = logging.getLogger(__name__)


class OpenWiFiConTask(Task):
  def __init__(self, eventTime: int, stats: dict, wificon: WiFiHandler):
    super().__init__(eventTime, stats)
    self.wificon = wificon

  def execute(self, eventTime):
    log.info('Opening WiFi connection to {}'.format(self.wificon.SSID))
    try:
      self.wificon.connect()
    except Exception as e:
      log.Error('Failed to connect to WiFi. Invalid SSID or PSK: ')
      log.exception(e)
      self.time = eventTime + 10000
      return self