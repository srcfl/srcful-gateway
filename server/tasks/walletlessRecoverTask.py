import datetime
import logging
import base58
import requests
from typing import List, Union, Tuple
import server.crypto.crypto as crypto
from server.blackboard import BlackBoard
from .itask import ITask


from .srcfulAPICallTask import SrcfulAPICallTask

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class WalletlessRecoverTask(SrcfulAPICallTask):
    def __init__(
        self, event_time: int, bb: BlackBoard, api_key: str, access_key: str):
        super().__init__(event_time, bb)
        self.prv = ""
        self.pub = ""
        self.post_url = "https://api.srcful.dev/"
        self.api_key = api_key
        self.access_key = access_key

    def _json(self):


        # {serial}|{access_key}|{DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")}

        with crypto.Chip() as chip:
            serial = chip.get_serial_number().hex()
            date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            message = f"{serial}|{self.access_key}|{date}"
            sign = chip.get_signature(message).hex()
        
        m = self._build_mutation(self.api_key, message, sign)

        return {"query": m}

    def _build_mutation(self, api_key: str, message: str, sign: str) -> str:
        m = """
            mutation {
                walletlessSigning {
                    recover(apiKey:"$var_api_key",deviceMessage:"$var_message", signature:"$var_sign"}) {
                        privateKey
                        publicKey
                    }
                }
            }
            """

        m = m.replace("$var_api_key", api_key)
        m = m.replace("$var_message", message)
        m = m.replace("$var_sign", sign)

        return m

    def _on_200(self, reply: requests.Response) -> Union[List[ITask], ITask, None]:
        self.prv = reply.json().get("data", {}).get("walletlessSigning", {}).get("recover", {})["privateKey"] or  ""
        self.pub = reply.json().get("data", {}).get("walletlessSigning", {}).get("recover", {})["publicKey"] or  ""
        
        return None

    def _on_error(self, reply: requests.Response) -> Union[int, Tuple[int, Union[List[ITask], ITask, None]]]:
        logger.warning("Failed to recover walletless keys")
        return 0
