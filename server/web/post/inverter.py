import json
import queue
from server.inverters.InverterTCP import InverterTCP
from server.inverters.InverterRTU import InverterRTU
from server.tasks.openInverterTask import OpenInverterTask

import logging
logger = logging.getLogger(__name__)

class Handler:

  def jsonSchema(self):
    return json.dumps({ 'type': 'post',
                        'description': 'open an inverter',
                        'required': {'ip': 'string, ip address of the inverter',
                                     'port': 'int, port of the inverter',
                                     'type': 'string, type of inverter',
                                     'address': 'int, address of the inverter'},
                        'returns': {'status': 'string, ok or error',
                                    'message': 'string, error message'}
                      })

  def doPost(self, post_data: dict, stats: dict, tasks: queue.Queue) -> tuple[int, str]:
    if 'ip' in post_data and 'port' in post_data and 'type' in post_data:
      try:
        if 'S0' in post_data['ip']:
          inverter = InverterRTU((post_data['ip'], post_data['type'], int(post_data['address'])))
          logger.info("Created an RTU inverter")
        else:
          inverter = InverterTCP((post_data['ip'], int(post_data['port']), post_data['type'], int(post_data['address'])))
          logger.info("Created a TCP inverter")
        
        tasks.put(OpenInverterTask(100, stats, inverter, stats['bootstrap']))
        return 200, json.dumps({'status': 'ok'})
      except Exception as e:
        logger.error('Failed to open inverter: {}'.format(post_data))
        logger.error(e)
        return 500, json.dumps({'status': 'error', 'message': str(e)})
    else:
      return 400, json.dumps({'status': 'bad request'})
