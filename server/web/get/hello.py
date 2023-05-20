import json
from typing import Callable

class Handler:
  def doGet(self, stats: dict, timeMSFunc: Callable, chipInfoFunc: Callable):
    # return the json data {'serial:' crypto.serial, 'pubkey': crypto.publicKey}
    ret = {'message': 'hello world from srcful!'}


    return 200, json.dumps(ret)