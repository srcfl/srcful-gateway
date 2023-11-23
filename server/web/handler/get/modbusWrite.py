import json
from typing import Callable
from ..handler import GetHandler

from ..requestData import RequestData

class Handler(GetHandler):
  def doGet(self, request_data: RequestData):  
    if('inverter' in request_data.stats and request_data.stats['inverter'] != None): 
      self.inverter = request_data.stats['inverter']
      if self.inverter.isOpen():
        ret = {'message': 'Inverter open'}
      else:
        ret = {'message': 'Inverter not open'}
    else:
      ret = {'message': 'No Inverter found...'}

    return 200, json.dumps(ret)