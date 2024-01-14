from ..handler import DeleteHandler
from ..requestData import RequestData
import json

class Handler(DeleteHandler):

    def schema(self):
        return { 'type': 'delete',
                        'description': 'Delete and remove the inverter, currently this does not affect the bootstrapping process',
                        'returns': {'isTerminated': 'bool, True if the inverter is terminated',
                                    'isOpen': 'bool, True if the inverter is open'}
                      }

    def doDelete(self, request_data: RequestData):
        if len(request_data.bb.inverters.lst) > 0:
            inverter = request_data.bb.inverters.lst[0]
            inverter.terminate()
            request_data.bb.inverters.remove(inverter)

            data = {'isTerminated': inverter.isTerminated(),
                    'isOpen': inverter.isOpen()}

            return 200, json.dumps(data)
        else:
            return 400, json.dumps({'error': 'no inverter initialized'})
    
        
                               