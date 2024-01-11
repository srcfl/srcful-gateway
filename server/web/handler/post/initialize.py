import queue
import json

import logging
logger = logging.getLogger(__name__)

from server.tasks.initializeTask import InitializeTask

from ..handler import PostHandler
from ..requestData import RequestData


class Handler(PostHandler):


  def schema(self):
    return { 'type': 'post',
                        'description': 'initialize the wallet',
                        'required': {'wallet': 'string, wallet public key'},
                        'returns': {'initialized': 'boolean, true if the wallet is initialized'}
                      }
  def jsonSchema(self):
    return json.dumps(self.schema())

  def doPost(self, request_data: RequestData):
    if 'wallet' in request_data.data:
      t = InitializeTask(0, {}, request_data.data['wallet'])
      t.execute(0)
      t.t.join()
      t.execute(0)

      if t.isInitialized is None:
        return t.response.status, json.dumps({"body": t.response.body})
      
      return 200, json.dumps({'initialized': t.isInitialized})
    else:
      return 400, json.dumps({'status': 'bad request'})
