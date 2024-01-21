from .srcfulAPICallTask import SrcfulAPICallTask

import server.crypto.crypto as atecc608b
from server.blackboard import BlackBoard
import requests

import logging

log = logging.getLogger(__name__)


class InitializeTask(SrcfulAPICallTask):
    def __init__(self, event_time: int, bb: BlackBoard, wallet: str):
        super().__init__(event_time, bb)
        self.isInitialized = None
        self.post_url = "https://api.srcful.dev/"
        self.wallet = wallet

    def _json(self):
        atecc608b.init_chip()
        serial = atecc608b.get_serial_number().hex()

        id_and_wallet = serial + ":" + self.wallet
        sign = atecc608b.get_signature(id_and_wallet).hex()
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

        m = m.replace("$var_idAndWallet", id_and_wallet)
        m = m.replace("$var_sign", sign)

        log.info("Preparing intialization of wallet %s with sn %s", self.wallet, serial)

        return {"query": m}

    def _on_200(self, reply: requests.Response):
        if (
            reply.json()["data"]["gatewayInception"] is not None
            and reply.json()["data"]["gatewayInception"]["initialize"] is not None
            and reply.json()["data"]["gatewayInception"]["initialize"]["initialized"]
            is not None
        ):
            self.isInitialized = reply.json()["data"]["gatewayInception"]["initialize"][
                "initialized"
            ]
        self.isInitialized = reply.json()["data"]["gatewayInception"]["initialize"][
            "initialized"
        ]
