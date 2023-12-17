import json
import queue
from server.inverters.InverterTCP import InverterTCP
from server.tasks.openInverterTask import OpenInverterTask

import logging
logger = logging.getLogger(__name__)

from ..handler import PostHandler
from ..requestData import RequestData

class Handler(PostHandler):

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

  def doPost(self, request_data:RequestData) -> tuple[int, str]:
    if 'ip' in request_data.data and 'port' in request_data.data and 'type' in request_data.data:
      try:
        conf = (request_data.data['ip'], int(request_data.data['port']), request_data.data['type'], int(request_data.data['address']))
        inverter = InverterTCP(conf)
        logger.info("Created a TCP inverter")
        
        request_data.tasks.put(OpenInverterTask(100, request_data.stats, inverter, request_data.stats['bootstrap']))
        return 200, json.dumps({'status': 'ok'})
      except Exception as e:
        logger.error('Failed to open inverter: {}'.format(request_data.data))
        logger.error(e)
        return 500, json.dumps({'status': 'error', 'message': str(e)})
    else:
      return 400, json.dumps({'status': 'bad request'})
    

