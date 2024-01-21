from .srcfulAPICallTask import SrcfulAPICallTask

import server.crypto.crypto as atecc608b
import requests

from server.blackboard import BlackBoard


class GetNameTask(SrcfulAPICallTask):
    """Task to get a name from the server using the crypto chip"""

    def __init__(self, event_time: int, bb: BlackBoard):
        super().__init__(event_time, bb)
        self.name = None
        self.post_url = "https://api.srcful.dev/"

    def _json(self):
        atecc608b.init_chip()
        serial = atecc608b.get_serial_number().hex()
        atecc608b.release()

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
        return 0

    def _on_200(self, reply: requests.Response):
        self.name = reply.json()["data"]["gatewayConfiguration"]["gatewayName"]["name"]
