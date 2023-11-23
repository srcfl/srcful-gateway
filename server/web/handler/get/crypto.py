import json
from typing import Callable
import server.crypto.crypto as crypto

from ..handler import GetHandler
from ..requestData import RequestData

class Handler(GetHandler):
  def doGet(self, data: RequestData):
    # return the json data {'serial:' crypto.serial, 'pubkey': crypto.publicKey}
    crypto.initChip()
    ret = crypto.getChipInfo()
    ret['publicKey_pem'] = crypto.publicKeyToPEM(crypto.getPublicKey())
    crypto.release()

    return 200, json.dumps(ret)
