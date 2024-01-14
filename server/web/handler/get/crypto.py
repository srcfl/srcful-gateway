import json
from typing import Callable
import server.crypto.crypto as crypto

from ..handler import GetHandler
from ..requestData import RequestData

class Handler(GetHandler):

  def schema(self):
    return { 'type': 'get',
                    'description': 'Get crypo chip information',
                    'returns': {'device': 'string, device name',
                                'serialNumber': 'string, serial number',
                                'publikKey': 'string, public key',
                                'publicKey_pem': 'string, public key in pem format'}
                  }

  def doGet(self, data: RequestData):
    # return the json data {'serial:' crypto.serial, 'pubkey': crypto.publicKey}
    crypto.initChip()
    ret = crypto.getChipInfo()
    ret['publicKey_pem'] = crypto.publicKeyToPEM(crypto.getPublicKey())
    crypto.release()

    return 200, json.dumps(ret)
