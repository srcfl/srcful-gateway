import queue
import json

from server.tasks.initializeTask import InitializeTask

class Handler:

  def jsonSchema(self):
    return json.dumps({ 'type': 'post',
                        'description': 'initialize the wallet',
                        'required': {'wallet': 'string, wallet public key'},
                        'returns': {'initialized': 'boolean, true if the wallet is initialized'}
                      })

  def doPost(self, post_data: dict, post_params:dict, stats: dict, tasks: queue.Queue):
    if 'wallet' in post_data:
      t = InitializeTask(0, {}, post_data['wallet'])
      t.execute(0)
      t.t.join()
      t.execute(0)

      if t.isInitialized is None:
        return t.response.status, json.dumps({"body": t.response.body})
      
      return 200, json.dumps({'initialized': t.isInitialized})
    else:
      return 400, json.dumps({'status': 'bad request'})
