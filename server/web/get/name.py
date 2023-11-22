import json
from typing import Callable
from server.tasks.getNameTask import GetNameTask

class Handler:
  def doGet(self, stats: dict, post_params:dict, timeMSFunc: Callable, chipInfoFunc: Callable):
    # return the json data {'serial:' crypto.serial, 'pubkey': crypto.publicKey}
    t = GetNameTask(0, {})
    t.execute(0)
    t.t.join()
    t.execute(0)

    if t.name is None:
      return t.response.status, json.dumps({"body": t.response.body})
    
    return 200, json.dumps({'name': t.name})