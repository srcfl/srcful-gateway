import json
from typing import Callable

class Handler:
  def doGet(self, stats: dict, timeMSFunc: Callable, chipInfoFunc: Callable):
    
    if('inverter' in stats and stats['inverter'] != None): 
      self.inverter = stats['inverter']
      if self.inverter.isOpen():
        ret = {'message': 'Inverter open'}
      else:
        ret = {'message': 'Inverter not open'}
    else:
      ret = {'message': 'No Inverter found...'}

    return 200, json.dumps(ret)