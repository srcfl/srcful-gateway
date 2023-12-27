import struct
import json
from typing import Callable
from ..handler import GetHandler

from ..requestData import RequestData

from server.inverters.inverter import Inverter

# Example query: inverter/modbus/holding/40069?size=2&type=float&endianess=big

class RegisterHandler(GetHandler):
    def doGet(self, request_data: RequestData):
        if 'address' not in request_data.post_params:
            return 400, json.dumps({'error': 'missing address'})
        if 'inverter' not in request_data.stats or request_data.stats['inverter'] is None:
            return 400, json.dumps({'error': 'inverter not initialized'})

        raw = bytearray()
        address = int(request_data.post_params['address'])
        size = int(request_data.query_params.get('size', 1))

        try:
            raw = self.get_registers(request_data.stats['inverter'], address, size)
            # from what I understand the modbus stuff returns a list of bytes, so we need to convert it to a bytearray
            raw = bytearray(raw)
            ret = {
                'register': address,
                'raw_value': raw.hex(),
            }
    
            if len(request_data.query_params) > 0:
                try:
                    
                    datatype = Inverter.RegisterType.from_str(request_data.query_params.get('type', 'uint'))
                    endianness = Inverter.RegisterEndianness.from_str(request_data.query_params.get('endianess', 'big'))
                    value = Inverter.formatValue(raw, datatype, endianness)
                    ret['value'] = value 
                except Exception as e:
                    return 400, json.dumps({'error': str(e)})

            return 200, json.dumps(ret)
        except Exception as e:
            return 400, json.dumps({'error': str(e)})

    def get_registers(self, inverter):
        raise NotImplementedError()


class HoldingHandler(RegisterHandler):
    def get_registers(self, inverter, address, size):
        return inverter.readHoldingRegister(address, size)

class InputHandler(RegisterHandler):
    def get_registers(self, inverter, address, size):
        return inverter.readInputRegister(address, size)
