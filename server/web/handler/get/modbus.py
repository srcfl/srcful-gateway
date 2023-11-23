import struct
import json
from typing import Callable
from ..handler import GetHandler

from ..requestData import RequestData

class RegisterHandler(GetHandler):
    def doGet(self, request_data: RequestData):
        if 'address' not in request_data.post_params:
            return 400, json.dumps({'error': 'missing address'})
        if 'inverter' not in request_data.stats or request_data.stats['inverter'] is None:
            return 400, json.dumps({'error': 'inverter not initialized'})

        registers = self.get_registers(request_data.stats['inverter'])

        raw_value = bytearray()
        address = int(request_data.post_params['address'])
        size = int(request_data.query_params.get('size', 1))
        for i in range(size):
            if address + i not in registers:
                return 400, json.dumps({'error': 'invalid or incomplete address range'})
            raw_value += registers[address + i]

        ret = {
            'register': address,
            'raw_value': raw_value.hex(),
        }
 
        if len(request_data.query_params) > 0:
            status_code, value = self.parse_params(raw_value, request_data.query_params)
            if status_code != 200:
                return status_code, value
            ret['value'] = value    

        return 200, json.dumps(ret)

    def get_registers(self, inverter):
        raise NotImplementedError()

    @staticmethod
    def parse_params(raw_value, query_params):
        data_type = query_params.get('type', 'uint')
        endianess = query_params.get('endianess', 'big')
        
        if endianess not in ['big', 'little']:
            return 400, json.dumps({'error': 'Invalid endianess. endianess must be big or little'})
        
        

        if data_type not in ['uint', 'int', 'float', 'ascii', 'utf16']:
            return 400, json.dumps({'error': 'Unknown datatype'})

        
        if data_type == 'uint':
            value = int.from_bytes(raw_value, byteorder=endianess, signed=False)
        elif data_type == 'int':
            value = int.from_bytes(raw_value, byteorder=endianess, signed=True)
        elif data_type == 'float':

            if endianess == 'big':
                endianess = '>'
            if endianess != '>':
                endianess = '<'

            if len(raw_value) == 4:
                value = struct.unpack(f'{endianess}f', raw_value)[0]
            elif len(raw_value) == 8:
                value = struct.unpack(f'{endianess}d', raw_value)[0]
        elif data_type == 'ascii':
            value = raw_value.decode('ascii')
        elif data_type == 'utf16':
            value = raw_value.decode('utf-16' + ('be' if endianess == 'big' else 'le'))

        return 200, value

class HoldingHandler(RegisterHandler):
    def get_registers(self, inverter):
        return inverter.readHoldingRegisters()

class InputHandler(RegisterHandler):
    def get_registers(self, inverter):
        return inverter.readInputRegisters()
