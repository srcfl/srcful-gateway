import struct
import json
from typing import Callable
from ..handler import GetHandler

from ..requestData import RequestData

from server.inverters.registeValue import RegisterValue

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
            registers = self.get_registers(request_data.stats['inverter'], address, size)

            # Convert to bytes and keep the endianness of each register (word)
            for register in registers:
                byte_arr = register.to_bytes(2, 'little')
                raw.extend(byte_arr)

            ret = {
                'register': address,
                'size': size,
                'raw_value': raw.hex(),
            }
    
            if len(request_data.query_params) > 0:
                try:
                    
                    datatype = RegisterValue.Type.from_str(request_data.query_params.get('type', 'uint'))
                    # Endianness, like other parameters, is device-specific. Consider breaking this out.
                    endianness = RegisterValue.Endianness.from_str(request_data.query_params.get('endianess', 'little'))
                    value = RegisterValue(address, size, datatype, endianness).getValue(raw)
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
        return inverter.readHoldingRegisters(address, size)

class InputHandler(RegisterHandler):
    def get_registers(self, inverter, address, size):
        return inverter.readInputRegisters(address, size)
