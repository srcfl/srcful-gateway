import json
import queue
from server.inverters.InverterRTU import InverterRTU
from server.tasks.openInverterTask import OpenInverterTask

import logging
logger = logging.getLogger(__name__)

class Handler:

  def jsonSchema(self):
    return json.dumps({ 'type': 'post',
                        'description': 'open an inverter',
                        'required': {'port': 'string, Serial port used for communication',
                                     'baudrate': 'int, Bits per second',
                                     'bytesize': 'int, Number of bits per byte 7-8',
                                     'parity': 'string, \'E\'ven, \'O\'dd or \'N\'one',
                                     'stopbits': 'float, Number of stop bits 1, 1.5, 2',
                                     'type': 'string, solaredge, huawei or fronius etc...',
                                     'address': 'int, Modbus address of the inverter',},
                        'returns': {'status': 'string, ok or error',
                                    'message': 'string, error message'}
                      })

  def doPost(self, post_data: dict, post_params:dict, stats: dict, tasks: queue.Queue) -> tuple[int, str]:
    if 'port' in post_data and 'type' in post_data:
      try:
        conf = (post_data['port'], 
                int(post_data['baudrate']), 
                int(post_data['bytesize']), 
                post_data['parity'], 
                float(post_data['stopbits']), 
                post_data['type'], 
                int(post_data['address']))
        self.inverter = InverterRTU(conf)
        logger.info("Created an RTU inverter")
        
        tasks.put(OpenInverterTask(100, stats, self.inverter, stats['bootstrap']))
        return 200, json.dumps({'status': 'ok'})
      except Exception as e:
        logger.error('Failed to open inverter: {}'.format(post_data))
        logger.error(e)
        return 500, json.dumps({'status': 'error', 'message': str(e)})
    else:
      return 400, json.dumps({'status': 'bad request'})
