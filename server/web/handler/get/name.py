import json
from typing import Callable
from server.tasks.getNameTask import GetNameTask

from ..handler import GetHandler

from ..requestData import RequestData

class Handler(GetHandler):
  def doGet(self, request_data: RequestData):  
    # this works as the web response task is threaded in itself and will not block
    # the task queue execution - afaik :P
    t = GetNameTask(0, {})
    t.execute(0)
    t.t.join()
    t.execute(0)

    if t.name is None:
      return t.response.status, json.dumps({"body": t.response.body})
    
    return 200, json.dumps({'name': t.name})