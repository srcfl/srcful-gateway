import json
from ..handler import GetHandler

from ..requestData import RequestData

class Handler(GetHandler):
  def doGet(self, request_data: RequestData):
    config = {'status': 'No inverter'}

    if('inverter' in request_data.stats and request_data.stats['inverter'] != None): 
      inverter = request_data.stats['inverter']
      config = inverter.getConfigDict()
    
      if inverter.isOpen():
        config['status'] = 'open'
      else:
        config['status'] = 'closed'
      

    return 200, json.dumps(config)