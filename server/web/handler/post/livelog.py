# this is the inverter live log post handler

import queue
import json
import logging


from ..requestData import RequestData

# this is the modbus love log post handler

class Handler:

    def jsonDict(self):
        return  {'type': 'post',
                'description': 'creates a new live log object',
                'required': {'frequency': 'how many samples per second',
                            'size': 'the size of the logging buffer, the buffer is circular so if the buffer is full the oldest data is overwritten',
                            'registers': 'a list of registers to log, each register is a dictionary with the following register: holding/input, keys: address, size, type, endianess',},
                'returns': {'object': 'a unique identifier for the live log object'}
                }
  
    def jsonSchema(self):
        return json.dumps(self.jsonDict())
    
    def doPost(self, request_data:RequestData):
        if 'inverter' not in request_data.stats or request_data.stats['inverter'] is None:
            return 400, json.dumps({'error': 'inverter not initialized'})

        if 'frequency' in request_data.data and 'size' in request_data.data and 'registers' in request_data.data:
            inverter = request_data.stats['inverter']
            if inverter.isOpen():
                # create a new live log object
                live_log = inverter.createLiveLog(request_data.data['frequency'], request_data.data['size'])
                # add the registers to the live log object
                for register in request_data.data['registers']:
                    live_log.addRegister(register['address'], register['size'], register['type'], register['endianess'])
                # start the live log
                live_log.start()
                # add the live log to the inverter
                inverter.addLiveLog(live_log)
                # return the live log object id
                return 200, json.dumps({'object': live_log.id})
            
            
        
        else:
            # return a bad request and append the json schema 
            return 400, json.dumps({'status': 'bad request', 'schema': self.jsonDict()}
