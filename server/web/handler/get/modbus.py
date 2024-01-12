import struct
import json
from typing import Callable
from ..handler import GetHandler

from ..requestData import RequestData

from server.inverters.registerValue import RegisterValue

# Example query: inverter/modbus/holding/40069?size=2&type=float&endianess=big

class RegisterHandler(GetHandler):
    def doGet(self, request_data: RequestData):
        if 'address' not in request_data.post_params:
            return 400, json.dumps({'error': 'missing address'})
        if len(request_data.bb.inverters.lst) == 0:
            return 400, json.dumps({'error': 'inverter not initialized'})

        raw = bytearray()
        address = int(request_data.post_params['address'])
        size = int(request_data.query_params.get('size', 1))

        try:
            datatype = RegisterValue.Type.from_str(request_data.query_params.get('type', 'none'))
            endianness = RegisterValue.Endianness.from_str(request_data.query_params.get('endianess', 'little'))  
            raw, value = RegisterValue(address, size, self.get_register_type(), datatype, endianness).readValue(request_data.bb.inverters.lst[0])
            

            ret = {
                'register': address,
                'size': size,
                'raw_value': raw.hex(),
            }
            if value != None:
                ret['value'] = value
    
            return 200, json.dumps(ret)
        except Exception as e:
            return 400, json.dumps({'error': str(e)})

    def get_register_type(self):
        raise NotImplementedError()


class HoldingHandler(RegisterHandler):
    def get_register_type(self):
        return RegisterValue.RegisterType.HOLDING

class InputHandler(RegisterHandler):
    def get_register_type(self):
        return RegisterValue.RegisterType.INPUT
