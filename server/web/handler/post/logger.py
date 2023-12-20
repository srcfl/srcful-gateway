import queue
import json
import logging


from ..requestData import RequestData

class Handler:

  def jsonDict(self):
    return {'type': 'post',
            'description': 'set the log level of a logger',
            'required': {'logger': 'string, name of logger i.e. server.web.server',
                        'level': 'string, name of level i.e. DEBUG, INFO, WARNING, ERROR, CRITICAL'},
            'returns': {'level': 'boolean, true if the logger was valid and the level was set'}
            }
  
  def jsonSchema(self):
    return json.dumps(self.jsonDict())

  def doPost(self, request_data:RequestData):
    if 'logger' in request_data.data and 'level' in request_data.data:
      # check that the logger and level are valid
        try:
            # check that the logger actually exits in the logging module - we cannot directl use getLogger as this will create the logger
            if request_data.data['logger'] != 'root' and request_data.data['logger'] not in logging.root.manager.loggerDict:
                return 200, json.dumps({'level': False})

            logger = logging.getLogger(request_data.data['logger'])
            level = logging.getLevelName(request_data.data['level'])
            logger.setLevel(level)
            return 200, json.dumps({'level': True})
        except Exception as e:
            logger.error('Failed to set logger level: {}'.format(request_data.data))
            logger.error(e)
            return 200, json.dumps({'level': False})
      
    else:
      # return a bad request and append the json schema 
      return 400, json.dumps({'status': 'bad request', 'schema': self.jsonDict()})