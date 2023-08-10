from .srcfulAPICallTask import SrcfulAPICallTask

import server.crypto.crypto as atecc608b
import requests


class GetNameTask(SrcfulAPICallTask):
  '''Task to get a name from the server using the crypto chip'''
    
  def __init__(self, eventTime: int, stats: dict):
    super().__init__(eventTime, stats)
    self.name = None
    self.post_url = "https://api.srcful.dev/"
    
  def _json(self):
    atecc608b.initChip()
    serial = atecc608b.getSerialNumber().hex()
    atecc608b.release()

    q = """{
        gatewayConfiguration {
          gatewayName(id:$var_serial) {
            name
          }
        }
      }"""
  
    q = q.replace('$var_serial', f'"{serial}"')

    return {'query': q}

  def _onError(self, reply: requests.Response) -> int:
    return 0
  
  def _on200(self, reply: requests.Response):
    self.name = reply.json()['data']['gatewayConfiguration']['gatewayName']['name']
        