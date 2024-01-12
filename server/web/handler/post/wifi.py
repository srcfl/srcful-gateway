import json
import queue
from server.wifi.wifi import WiFiHandler
from server.tasks.openWiFiConTask import OpenWiFiConTask

import logging
log = logging.getLogger(__name__)


from ..handler import PostHandler
from ..requestData import RequestData

class Handler(PostHandler):

  def schema(self):
    return { 'type': 'post',
                        'description': 'open a wifi connection',
                        'required': {'ssid': 'string, ssid of the wifi',
                                     'psk': 'string, password of the wifi'},
                        'returns': {'status': 'string, ok or error',
                                    'message': 'string, error message'}
                      }
  def jsonSchema(self):
    return json.dumps(self.schema())

  def doPost(self, request_data:RequestData) -> tuple[int, str]:
    if 'ssid' in request_data.data and 'psk' in request_data.data:
      try:
        log.info('Opening WiFi connection to {}'.format(request_data.data['ssid']))
        wificon = WiFiHandler(request_data.data['ssid'], request_data.data['psk'])
        request_data.tasks.put(OpenWiFiConTask(1000, request_data.bb, wificon))
        return 200, json.dumps({'status': 'ok'})
      except Exception as e:
        return 500, json.dumps({'status': 'error', 'message': str(e)})
    else:
      return 400, json.dumps({'status': 'bad request'})