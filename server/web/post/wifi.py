import json
import queue
from server.wifi.wifi import WiFiHandler
from server.tasks.openWiFiConTask import OpenWiFiConTask

class Handler:

  def doPost(self, post_data: dict, stats: dict, tasks: queue.Queue) -> tuple[int, str]:
    if 'ssid' in post_data and 'psk' in post_data:
      try:
        wificon = WiFiHandler(post_data['ssid'], post_data['psk'])
        tasks.put(OpenWiFiConTask(100, stats, wificon))
        return 200, json.dumps({'status': 'ok'})
      except Exception as e:
        return 500, json.dumps({'status': 'error', 'message': str(e)})
    else:
      return 400, json.dumps({'status': 'bad request'})