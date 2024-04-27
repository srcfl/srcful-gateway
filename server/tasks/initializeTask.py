import logging
import requests

import server.crypto.crypto as crypto
from server.blackboard import BlackBoard

from .srcfulAPICallTask import SrcfulAPICallTask

log = logging.getLogger(__name__)


class InitializeTask(SrcfulAPICallTask):
    def __init__(
        self, event_time: int, bb: BlackBoard, wallet: str, dry_run: bool = False
    ):
        super().__init__(event_time, bb)
        self.is_initialized = None
        self.post_url = "https://api.srcful.dev/"
        self.wallet = wallet
        self.dry_run = dry_run

    def _json(self):
        with crypto.Chip() as chip:
            serial = chip.get_serial_number().hex()
            pub_key = chip.get_public_key().hex()

            id_and_wallet = serial + ":" + self.wallet + ":" + pub_key
            sign = chip.get_signature(id_and_wallet).hex()
        
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

        if self.dry_run:
            m = m.replace(
                "gatewayInitialization:{idAndWallet",
                "gatewayInitialization:{dryRun:true, idAndWallet",
            )

        log.info("Preparing intialization of wallet %s with sn %s", self.wallet, serial)

        return {"query": m}

    def _on_200(self, reply: requests.Response):
        if (
            reply.json()["data"]["gatewayInception"] is not None
            and reply.json()["data"]["gatewayInception"]["initialize"] is not None
            and reply.json()["data"]["gatewayInception"]["initialize"]["initialized"]
            is not None
        ):
            self.is_initialized = reply.json()["data"]["gatewayInception"][
                "initialize"
            ]["initialized"]
        self.is_initialized = reply.json()["data"]["gatewayInception"]["initialize"][
            "initialized"
        ]

    def _on_error(self, reply: requests.Response) -> int:
        log.warning("Failed to initialize wallet %s", self.wallet)
        return 0
