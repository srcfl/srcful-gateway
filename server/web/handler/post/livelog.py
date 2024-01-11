# this is the inverter live log post handler

import queue
import json
import logging

import server.inverters.registerValue as RegisterValue


from ..requestData import RequestData

# this is the modbus live log post handler

class Handler:

    def schema(self):
        return  {
                'status': 'under development',
                'type': 'post',
                'description': 'creates a new live log object',
                'required': {'frequency': 'how many samples per second',
                            'size': 'the size of the logging buffer, the buffer is circular so if the buffer is full the oldest data is overwritten',
                            'registers': 'a list of registers to log, each register is a dictionary with the following register: holding/input, keys: address, size, type, endianess',},
                'returns': {'object': 'a unique identifier for the live log object'}
                }
  
    def jsonSchema(self):
        return json.dumps(self.schema())
    
    def doPost(self, request_data:RequestData):
        if 'inverter' not in request_data.stats or request_data.stats['inverter'] is None:
            return 400, json.dumps({'error': 'inverter not initialized'})

        if 'frequency' in request_data.data and 'size' in request_data.data and 'registers' in request_data.data:
            inverter = request_data.stats['inverter']
            if inverter.isOpen():
                # create a new live log object
                registerValues = []
                for register in request_data.data['registers']:
                    try:
                        registerType = RegisterValue.RegisterType.from_str(register['register'])
                        dataType = RegisterValue.Type.from_str(register['type'])
                        endianess = RegisterValue.Endianness.from_str(register['endianess'])
                        registerValues.append(RegisterValue(register['address'], register['size'], registerType, dataType, endianess))
                    except Exception as e:
                        return 400, json.dumps({'error': str(e)})
            else:
                return 400, json.dumps({'error': 'inverter not open'})
        else:
            # return a bad request and append the json schema 
            return 400, json.dumps({'status': 'bad request', 'schema': self.schema()})
