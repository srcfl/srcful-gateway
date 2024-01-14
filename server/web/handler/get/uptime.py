import json
from server.tasks.getNameTask import GetNameTask

from ..handler import GetHandler

from ..requestData import RequestData

class Handler(GetHandler):

  def schema(self):
    return { 'type': 'get',
                    'description': 'Get crypo chip information',
                    'returns': {'device': 'string, device name',
                                'serialNumber': 'string, serial number',
                                'publikKey': 'string, public key',
                                'publicKey_pem': 'string, public key in pem format'}
                  }


  def doGet(self, request_data: RequestData):  
    
    return 200, json.dumps({'msek': request_data.bb.time_ms() - request_data.bb.startTime})