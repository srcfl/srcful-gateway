from .srcfulAPICallTask import SrcfulAPICallTask

import server.crypto.crypto as atecc608b
import requests

class IntializeTask(SrcFulAPICallTask):
  
  def __init__(self, eventTime: int, stats: dict, wallet: str):
    super().__init__(eventTime, stats)
    self.name = None
    self.post_url = "https://api.srcful.dev/"
    self.wallet = str

  def _json(self):
    atecc608b.initChip()
    serial = atecc608b.getSerialNumber().hex()

    idAndWallet = serial + ':' + self.wallet
    sign = atecc608b.base64UrlEncode(atecc608b.getSignature(idAndWallet))
    atecc608b.release()

    m = """
    {
      gatewayInception {
        initialize(gatewayInitialization:{idAndWallet:"$var_idAndWallet", signature:"$var_sign"}) {
          initialized
        }
      }
    } """

    m = m.replace('$var_idAndWallet', idAndWallet)
    m = m.replace('$var_sign', sign)

    return {'mutation': m}
  
  def on200(self, reply: requests.Response):
    self.name = reply.json()['data']['gatewayInception']['initialize']['initialized']