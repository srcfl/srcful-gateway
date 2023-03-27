import json
import queue
from server.inverters.InverterTCP import InverterTCP
from server.tasks.openInverterTask import OpenInverterTask

class Handler:

  def doPost(self, post_data:dict, stats:dict, tasks:queue.Queue) -> tuple[int, str]:
    if 'ip' in post_data and 'port' in post_data and 'type' in post_data:
      try:
        inverter = InverterTCP((post_data['ip'], int(post_data['port']), post_data['type']))
        tasks.put(OpenInverterTask(100, stats, inverter))
        return 200, json.dumps({'status': 'ok'})
      except Exception as e:
        print(e)
        return 500, json.dumps({'status': 'error', 'message': str(e)})
    else:
      return 400, json.dumps({'status': 'bad request'})