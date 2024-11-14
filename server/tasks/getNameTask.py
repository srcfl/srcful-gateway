import requests

import server.crypto.crypto as crypto
from server.app.blackboard import BlackBoard

from .srcfulAPICallTask import SrcfulAPICallTask


class GetNameTask(SrcfulAPICallTask):
    """Task to get a name from the server using the crypto chip"""

    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        self.name = None
        self.post_url = "https://api.srcful.dev/"

    def _json(self):
        try:
            with crypto.Chip() as chip:
                serial = chip.get_serial_number().hex()
        except crypto.Chip.Error:
            serial = "0000000000000000"

        q = """{
        gatewayConfiguration {
          gatewayName(id:$var_serial) {
            name
          }
        }
      }"""

        q = q.replace("$var_serial", f'"{serial}"')

        return {"query": q}

    def _on_error(self, reply: requests.Response) -> int:
        self.name = None
        return 0

    def _on_200(self, reply: requests.Response):
        self.name = reply.json()["data"]["gatewayConfiguration"]["gatewayName"]["name"]
