import json
from typing import Callable

# this one should read the modbus holding register and return the value
class HoldingHandler:
  def doGet(self, stats: dict, post_params:dict, timeMSFunc: Callable, chipInfoFunc: Callable):
    if 'address' not in post_params:
      return 400, json.dumps({'error': 'missing address'})
    if stats['inverter'] is None:
        return 400, json.dumps({'error': 'inverter not initialized'})

    # return the json data {'serial:' crypto.serial, 'pubkey': crypto.publicKey}
    ret = {'register': post_params['address'],
           'raw_value': stats['inverter'].getHoldingRegister(int(post_params['address']))}


    return 200, json.dumps(ret)