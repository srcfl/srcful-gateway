import struct
import json

class HoldingHandler:
    def doGet(self, stats: dict, post_params:dict, query_params:dict, timeMSFunc: Callable, chipInfoFunc: Callable):
        if 'address' not in post_params:
            return 400, json.dumps({'error': 'missing address'})
        if stats['inverter'] is None:
            return 400, json.dumps({'error': 'inverter not initialized'})
    
        holdings = stats['inverter'].readHoldingRegisters()

        if post_params['address'] not in holdings:
            return 400, json.dumps({'error': 'invalid address'})

        # return the json data {'serial:' crypto.serial, 'pubkey': crypto.publicKey}
        ret = {'register': post_params['address'],
                'raw_value': holdings[post_params['address']]}

        if len(query_params) > 0:
            status_code, value = self.parse_params(holdings, post_params, query_params)
            if status_code != 200:
                return status_code, value
            ret['value'] = value

        return 200, json.dumps(ret)

    @staticmethod
    def parse_params(holdings, post_params, query_params):
        data_type = query_params.get('type')
        size = int(query_params.get('size', 0))
        endianess = query_params.get('endianess', 'big')

        if data_type not in ['uint', 'int', 'float']:
            return 400, json.dumps({'error': 'Unknown datatype'})

        if size not in [1, 2, 4, 8]:
            return 400, json.dumps({'error': 'Invalid size. Size must be 1, 2, 4, or 8'})

        if endianess not in ['big', 'little']:
            return 400, json.dumps({'error': 'Invalid endianess. endianess must be big or little'})

        raw_value = holdings[post_params['address']]

        if data_type == 'uint':
            value = int.from_bytes(raw_value, byteorder=endianess, signed=False)
        elif data_type == 'int':
            value = int.from_bytes(raw_value, byteorder=endianess, signed=True)
        elif data_type == 'float':
            if size == 4:
                value = struct.unpack('f', raw_value)[0]
            elif size == 8:
                value = struct.unpack('d', raw_value)[0]

        return 200, value
