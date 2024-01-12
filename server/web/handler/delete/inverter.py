from ..handler import DeleteHandler
from ..requestData import RequestData
import json

class Handler(DeleteHandler):
    def doDelete(self, request_data: RequestData):
        if len(request_data.bb.inverters.lst) > 0:
            inverter = request_data.inverters.inverters[0]
            inverter.terminate()
            request_data.inverters.remove(inverter)

            data = {'isTerminated': inverter.isTerminated(),
                    'isOpen': inverter.isOpen()}

            return 200, json.dumps(data)
        else:
            return 400, json.dumps({'error': 'no inverter initialized'})
    
        
                               