from .srcfulAPICallTask import SrcfulAPICallTask

import server.crypto.crypto as atecc608b
from server.blackboard import BlackBoard
import requests

import logging
log = logging.getLogger(__name__)

class InitializeTask(SrcfulAPICallTask):
  
  def __init__(self, eventTime: int, bb: BlackBoard, wallet: str):
    super().__init__(eventTime, bb)
    self.isInitialized = None
    self.post_url = "https://api.srcful.dev/"
    self.wallet = wallet

  def _json(self):
    atecc608b.initChip()
    serial = atecc608b.getSerialNumber().hex()

    idAndWallet = serial + ':' + self.wallet
    sign = atecc608b.getSignature(idAndWallet).hex()
    atecc608b.release()

    m = """
    mutation {
      gatewayInception {
        initialize(gatewayInitialization:{idAndWallet:"$var_idAndWallet", signature:"$var_sign"}) {
          initialized
        }
      }
    }
    """

    m = m.replace('$var_idAndWallet', idAndWallet)
    m = m.replace('$var_sign', sign)

    log.info('Preparing intialization of wallet %s with sn %s', self.wallet, serial)

    return {'query': m}
  
  def _on200(self, reply: requests.Response):
    if  reply.json()['data']['gatewayInception'] != None and \
        reply.json()['data']['gatewayInception']['initialize'] != None and \
        reply.json()['data']['gatewayInception']['initialize']['initialized'] != None:
          self.isInitialized = reply.json()['data']['gatewayInception']['initialize']['initialized']
    self.isInitialized = reply.json()['data']['gatewayInception']['initialize']['initialized']