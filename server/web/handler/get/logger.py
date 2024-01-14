import json
import logging
from typing import Callable
from ..handler import GetHandler

from ..requestData import RequestData

class Handler(GetHandler):
  
  def schema(self):
    return { 'type': 'get',
                    'description': 'Returns the configuration of the running inverter, details depend on the inverter type.',
                    'returns': {'A dictionary with all log names and their respective log level (DEGUG, INFO, WARNING, ERROR, CRITICAL)'}
                    }


  def doGet(self, request_data: RequestData):    
    loggers = [logging.getLogger()]  # get the root logger
    loggers = loggers + [logging.getLogger(name) for name in logging.root.manager.loggerDict]

    # create a json object with all the loggers
    ret = {}
    for logger in loggers:
        # if the logging is not set then get then recursively get the parent's level until one is found and append (inherited)
        if logger.level == logging.NOTSET:
            parent = logger.parent
            while parent.level == logging.NOTSET:
                parent = parent.parent
            ret[logger.name] = logging.getLevelName(parent.level) + ' (inherited)'
        else:
            ret[logger.name] = logging.getLevelName(logger.level)

    return 200, json.dumps(ret)