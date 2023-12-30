from ..handler import DeleteHandler
from ..requestData import RequestData
import json

class Handler(DeleteHandler):
    def doDelete(self, request_data: RequestData):
        if 'inverter' in request_data.stats and request_data.stats['inverter'] != None:
            inverter = request_data.stats['inverter']
            inverter.terminate()
            request_data.stats['inverter'] = None

            data = {'isTerminated': inverter.isTerminated(),
                    'isOpen': inverter.isOpen()}

            return 200, json.dumps(data)
        else:
            return 400, json.dumps({'error': 'no inverter initialized'})
    
        
                               