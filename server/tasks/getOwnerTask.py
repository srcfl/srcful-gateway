import requests

import server.crypto.crypto as crypto
from server.app.blackboard import BlackBoard

from .srcfulAPICallTask import SrcfulAPICallTask


class GetOwnerTask(SrcfulAPICallTask):
    """Task to get the owner wallet address from the server using the crypto chip"""

    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        self.wallet = None
        self.post_url = "https://api.srcful.dev/"

    def _json(self):
        try:
            with crypto.Chip() as chip:
                serial = chip.get_serial_number().hex()
        except crypto.ChipError:
            return

        q = """{
        gateway{
          gateway(id:$var_serial) {
            wallet
          }
        }
      }"""

        q = q.replace("$var_serial", f'"{serial}"')

        return {"query": q}

    def _on_error(self, reply: requests.Response) -> int:
        self.wallet = None
        return 0

    def _on_200(self, reply: requests.Response):
        self.wallet = reply.json()["data"]["gateway"]["gateway"]["wallet"]

    def get_result(self):
        """Return the wallet address in the requested format"""
        if self.wallet is not None:
            return {"wallet": self.wallet}
        return None
