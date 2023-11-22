import struct
import json
from typing import Callable

class HoldingHandler:
    def doGet(self, stats: dict, post_params:dict, query_params:dict, timeMSFunc: Callable, chipInfoFunc: Callable):
        if 'address' not in post_params:
            return 400, json.dumps({'error': 'missing address'})
        if stats['inverter'] is None:
            return 400, json.dumps({'error': 'inverter not initialized'})

        holdings = stats['inverter'].readHoldingRegisters()

        # Combine bytes from all addresses in the range post_params['address'] to post_params['address'] + size
        raw_value = bytearray()
        address = int(post_params['address'])  # convert address to integer
        size = int(query_params.get('size', 1))
        for i in range(size):
            if address + i not in holdings:
                return 400, json.dumps({'error': 'invalid or incomplete address range'})
            raw_value += holdings[address + i]

        ret = {
            'register': address,
            'raw_value': raw_value.hex(),  # Showcase raw_value as a hexadecimal string in the response
        }
 
        if len(query_params) > 0:
            status_code, value = self.parse_params(raw_value, query_params)
            if status_code != 200:
                return status_code, value
            ret['value'] = value    

        return 200, json.dumps(ret)

    @staticmethod
    def parse_params(raw_value, query_params):
        data_type = query_params.get('type', 'uint')
        endianess = query_params.get('endianess', 'big')

        if data_type not in ['uint', 'int', 'float', 'ascii', 'utf16']:
            return 400, json.dumps({'error': 'Unknown datatype'})

        if endianess not in ['big', 'little']:
            return 400, json.dumps({'error': 'Invalid endianess. endianess must be big or little'})

        if data_type == 'uint':
            value = int.from_bytes(raw_value, byteorder=endianess, signed=False)
        elif data_type == 'int':
            value = int.from_bytes(raw_value, byteorder=endianess, signed=True)
        elif data_type == 'float':
            if len(raw_value) == 4:
                value = struct.unpack(f'{endianess[0]}f', raw_value)[0]
            elif len(raw_value) == 8:
                value = struct.unpack(f'{endianess[0]}d', raw_value)[0]
        elif data_type == 'ascii':
            value = raw_value.decode('ascii')
        elif data_type == 'utf16':
            value = raw_value.decode('utf-16' + ('be' if endianess == 'big' else 'le'))

        return 200, value
