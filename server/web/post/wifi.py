import json
import queue
from server.wifi.wifi import WiFiHandler
from server.tasks.openWiFiConTask import OpenWiFiConTask

import logging
log = logging.getLogger(__name__)

class Handler:

  def jsonSchema(self):
    return json.dumps({ 'type': 'post',
                        'description': 'open a wifi connection',
                        'required': {'ssid': 'string, ssid of the wifi',
                                     'psk': 'string, password of the wifi'},
                        'returns': {'status': 'string, ok or error',
                                    'message': 'string, error message'}
                      })

  def doPost(self, post_data: dict, post_params:dict, stats: dict, tasks: queue.Queue) -> tuple[int, str]:
    if 'ssid' in post_data and 'psk' in post_data:
      try:
        log.info('Opening WiFi connection to {}'.format(post_data['ssid']))
        wificon = WiFiHandler(post_data['ssid'], post_data['psk'])
        tasks.put(OpenWiFiConTask(1000, stats, wificon))
        return 200, json.dumps({'status': 'ok'})
      except Exception as e:
        return 500, json.dumps({'status': 'error', 'message': str(e)})
    else:
      return 400, json.dumps({'status': 'bad request'})