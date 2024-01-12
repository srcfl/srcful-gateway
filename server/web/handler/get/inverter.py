import json
from ..handler import GetHandler

from ..requestData import RequestData

class Handler(GetHandler):
  def doGet(self, request_data: RequestData):
    config = {'status': 'No inverter'}

    if len(request_data.bb.inverters.lst) > 0:
      inverter = request_data.bb.inverters.lst[0]
      config = inverter.getConfigDict()
    
      if inverter.isOpen():
        config['status'] = 'open'
      else:
        config['status'] = 'closed'
      

    return 200, json.dumps(config)