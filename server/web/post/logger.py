import queue
import json
import logging


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

  def doPost(self, post_data: dict, stats: dict, tasks: queue.Queue):
    if 'logger' in post_data and 'level' in post_data:
      # check that the logger and level are valid
        try:
            # check that the logger actually exits in the logging module - we cannot directl use getLogger as this will create the logger
            if post_data['logger'] != 'root' and post_data['logger'] not in logging.root.manager.loggerDict:
                return 200, json.dumps({'level': False})

            logger = logging.getLogger(post_data['logger'])
            level = logging.getLevelName(post_data['level'])
            logger.setLevel(level)
            return 200, json.dumps({'level': True})
        except Exception as e:
            logger.error('Failed to set logger level: {}'.format(post_data))
            logger.error(e)
            return 200, json.dumps({'level': False})
      
    else:
      # return a bad request and append the json schema 
      return 400, json.dumps({'status': 'bad request', 'schema': self.jsonDict()})